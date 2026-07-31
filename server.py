from flask import Flask, request, jsonify, render_template, send_from_directory, Response, abort
import requests
from pathlib import Path
from macro_engine import apply_macros
from qr import generate_qr
from result_view import show_result
from clickhouse_client import check_redash_connection
from config import (
    RESULT_PROXY_TIMEOUT,
    RESULT_PROXY_TOKEN,
    RESULT_PROXY_URL,
    RESULT_VIEWER_URL,
)

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent


@app.route("/")
def home():
    return render_template(
        "index.html",
        result_proxy_enabled=bool(RESULT_PROXY_URL),
        result_viewer_url=RESULT_VIEWER_URL,
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

    if RESULT_PROXY_URL:
        headers = {"Content-Type": "application/json"}
        if RESULT_PROXY_TOKEN:
            headers["Authorization"] = f"Bearer {RESULT_PROXY_TOKEN}"

        try:
            response = requests.post(
                f"{RESULT_PROXY_URL}/proxy-check",
                headers=headers,
                json={},
                timeout=RESULT_PROXY_TIMEOUT,
            )
        except requests.RequestException as exc:
            app.logger.exception("Proxy request failed")
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
        res = show_result()
    except Exception as e:
        app.logger.exception("Redash check failed")
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

    result = check_redash_connection()
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


@app.route("/downloads/macos-result-viewer.zip", methods=["GET"])
def download_macos_result_viewer():
    downloads_dir = BASE_DIR / "distribution"
    return send_from_directory(downloads_dir, "macos-result-viewer.zip", as_attachment=True)


# -------- iOS enterprise (in-house) OTA distribution --------
IOS_DIR = BASE_DIR / "distribution" / "ios"
IOS_IPA_NAME = "mmptest.ipa"
IOS_BUNDLE_ID = "com.mmp.testtool.ios2"
IOS_APP_TITLE = "MMP Test Tool"
IOS_APP_VERSION = "1.0"


def _https_base():
    # itms-services requires HTTPS; Render terminates TLS so force the scheme.
    return "https://" + request.host


@app.route("/downloads/ios/mmptest.ipa", methods=["GET"])
def ios_ipa():
    if not (IOS_DIR / IOS_IPA_NAME).exists():
        abort(404, description="IPA not uploaded yet")
    return send_from_directory(IOS_DIR, IOS_IPA_NAME, as_attachment=True,
                               mimetype="application/octet-stream")


@app.route("/downloads/ios/manifest.plist", methods=["GET"])
def ios_manifest():
    ipa_url = f"{_https_base()}/downloads/ios/mmptest.ipa"
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>items</key>
  <array>
    <dict>
      <key>assets</key>
      <array>
        <dict>
          <key>kind</key><string>software-package</string>
          <key>url</key><string>{ipa_url}</string>
        </dict>
      </array>
      <key>metadata</key>
      <dict>
        <key>bundle-identifier</key><string>{IOS_BUNDLE_ID}</string>
        <key>bundle-version</key><string>{IOS_APP_VERSION}</string>
        <key>kind</key><string>software</string>
        <key>title</key><string>{IOS_APP_TITLE}</string>
      </dict>
    </dict>
  </array>
</dict>
</plist>
"""
    return Response(plist, mimetype="text/xml")


@app.route("/install/ios", methods=["GET"])
def install_ios():
    manifest_url = f"{_https_base()}/downloads/ios/manifest.plist"
    itms = f"itms-services://?action=download-manifest&amp;url={manifest_url}"
    ready = (IOS_DIR / IOS_IPA_NAME).exists()
    button = (
        f'<a class="btn" href="{itms}">Install {IOS_APP_TITLE}</a>'
        if ready else
        '<p style="color:#b00">Build not uploaded yet. Check back shortly.</p>'
    )
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Install {IOS_APP_TITLE}</title>
<style>
 body{{font-family:-apple-system,Helvetica,Arial,sans-serif;background:#f5f7fb;
      display:flex;min-height:90vh;align-items:center;justify-content:center;text-align:center;padding:20px}}
 .card{{background:#fff;border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.08);padding:32px;max-width:420px}}
 h1{{font-size:22px;margin:0 0 8px}} p{{color:#555;font-size:15px;line-height:1.5}}
 .btn{{display:inline-block;margin-top:16px;background:#0d6efd;color:#fff;text-decoration:none;
      padding:14px 28px;border-radius:999px;font-weight:600;font-size:17px}}
</style></head>
<body><div class="card">
 <h1>{IOS_APP_TITLE}</h1>
 <p>Open this page in <b>Safari</b> on your iPhone, then tap Install. Approve the install prompt; the app appears on your Home Screen.</p>
 {button}
 <p style="font-size:12px;color:#999;margin-top:20px">Aarki in-house app. If install doesn't start, ensure you opened this in Safari.</p>
</div></body></html>
"""
    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
