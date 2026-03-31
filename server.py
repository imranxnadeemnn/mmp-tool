from flask import Flask, request, jsonify, render_template
from macro_engine import apply_macros
from qr import generate_qr
from result_view import show_result

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
        return jsonify({"status": "error", "message": str(e)})

    if res is None:
        return jsonify({"status": "empty"})

    if isinstance(res, str):
        return jsonify({"status": "error", "message": res})

    return jsonify({
        "status": "success",
        "data": res.to_dict(orient="records")
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)