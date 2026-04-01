from flask import Flask, request, jsonify, render_template
from macro_engine import apply_macros
from qr import generate_qr
from result_view import show_result
from clickhouse_client import check_redash_connection

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


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

    data = request.json
    adid = data.get("advertising_id")

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
