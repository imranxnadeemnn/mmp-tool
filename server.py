from flask import Flask, request, jsonify, render_template
import requests
from macro_engine import apply_macros
from qr import generate_qr
from result_view import show_result
from clickhouse_client import check_redash_connection
from config import (
    RESULT_PROXY_TIMEOUT,
    RESULT_PROXY_TOKEN,
    RESULT_PROXY_URL,
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template(
        "index.html",
        result_proxy_enabled=bool(RESULT_PROXY_URL),
    )


# -------- Generate URL --------
@app.route("/generate", methods=["POST"])
def generate():

    data = request.json

    tracking_url = data.get("tracking_url")
    platform = data.get("platform")

    final_url = apply_macros(tracking_url, platform)
    qr_path = generate_qr(final_url)

    return jsonify({
        "final_url": final_url,
        "qr_path": qr_path
    })


# -------- Check Result --------
@app.route("/check", methods=["POST"])
def check():

    data = request.json or {}
    adid = data.get("advertising_id")

    if RESULT_PROXY_URL:
        headers = {"Content-Type": "application/json"}
        if RESULT_PROXY_TOKEN:
            headers["Authorization"] = f"Bearer {RESULT_PROXY_TOKEN}"

        try:
            response = requests.post(
                f"{RESULT_PROXY_URL}/proxy-check",
                headers=headers,
                json={"advertising_id": adid},
                timeout=RESULT_PROXY_TIMEOUT,
            )
        except requests.RequestException as exc:
            app.logger.exception("Proxy request failed for advertising_id=%s", adid)
            return jsonify({
                "status": "error",
                "message": f"Unable to reach internal VPN proxy: {exc}",
            }), 502

        try:
            proxy_data = response.json()
        except ValueError:
            proxy_data = {
                "status": "error",
                "message": f"Proxy returned non-JSON response ({response.status_code})",
            }

        return jsonify(proxy_data), response.status_code

    try:
        res = show_result(adid)
    except Exception as e:
        app.logger.exception("Redash check failed for advertising_id=%s", adid)
        return jsonify({"status": "error", "message": str(e)})

    if res is None:
        return jsonify({"status": "empty"})

    if isinstance(res, str):
        return jsonify({"status": "error", "message": res})

    return jsonify({
        "status": "success",
        "data": res.to_dict(orient="records")
    })


@app.route("/debug/redash", methods=["POST"])
def debug_redash():

    data = request.json or {}
    adid = data.get("advertising_id")

    if not adid:
        return jsonify({
            "status": "error",
            "message": "advertising_id is required"
        }), 400

    result = check_redash_connection(adid)
    status_code = 200 if result.get("ok") else 502
    return jsonify(result), status_code


@app.route("/debug/proxy", methods=["GET"])
def debug_proxy():
    if not RESULT_PROXY_URL:
        return jsonify({
            "ok": False,
            "message": "RESULT_PROXY_URL is not configured",
        }), 400

    headers = {}
    if RESULT_PROXY_TOKEN:
        headers["Authorization"] = f"Bearer {RESULT_PROXY_TOKEN}"

    try:
        response = requests.get(
            f"{RESULT_PROXY_URL}/health",
            headers=headers,
            timeout=RESULT_PROXY_TIMEOUT,
        )
    except requests.RequestException as exc:
        return jsonify({
            "ok": False,
            "message": f"Unable to reach proxy: {exc}",
            "proxy_url": RESULT_PROXY_URL,
        }), 502

    payload = {
        "ok": response.ok,
        "status_code": response.status_code,
        "proxy_url": RESULT_PROXY_URL,
    }
    try:
        payload["body"] = response.json()
    except ValueError:
        payload["body"] = response.text

    return jsonify(payload), (200 if response.ok else 502)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
