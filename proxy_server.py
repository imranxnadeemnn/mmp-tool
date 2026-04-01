import os
import time

import requests
from flask import Flask, jsonify, request


REDASH_URL = os.getenv("REDASH_URL", "https://redash.aarki.org").rstrip("/")
API_KEY = os.getenv("REDASH_API_KEY", os.getenv("API_KEY", ""))
QUERY_ID = int(os.getenv("REDASH_QUERY_ID", "28702"))
PROXY_AUTH_TOKEN = os.getenv("PROXY_AUTH_TOKEN", "")
REQUEST_TIMEOUT = int(os.getenv("REDASH_REQUEST_TIMEOUT", "10"))
POLL_TIMEOUT = int(os.getenv("REDASH_POLL_TIMEOUT", "20"))
POLL_INTERVAL = float(os.getenv("REDASH_POLL_INTERVAL", "1"))

headers = {
    "Authorization": f"Key {API_KEY}"
}

app = Flask(__name__)


def is_authorized():
    if not PROXY_AUTH_TOKEN:
        return True

    auth_header = request.headers.get("Authorization", "")
    return auth_header == f"Bearer {PROXY_AUTH_TOKEN}"


def unauthorized_response():
    return jsonify({"status": "error", "message": "Unauthorized"}), 401


@app.route("/health", methods=["GET"])
def health():
    if not is_authorized():
        return unauthorized_response()

    if not API_KEY:
        return jsonify({
            "status": "error",
            "message": "REDASH_API_KEY is not configured",
            "redash_url": REDASH_URL,
            "query_id": QUERY_ID,
        }), 500

    return jsonify({
        "status": "ok",
        "redash_url": REDASH_URL,
        "query_id": QUERY_ID,
    })


@app.route("/proxy-check", methods=["POST"])
def proxy_check():
    if not is_authorized():
        return unauthorized_response()

    data = request.json or {}
    adid = data.get("advertising_id")

    if not adid:
        return jsonify({"status": "error", "message": "advertising_id is required"}), 400

    if not API_KEY:
        return jsonify({"status": "error", "message": "REDASH_API_KEY is not configured"}), 500

    try:
        url = f"{REDASH_URL}/api/queries/{QUERY_ID}/results"
        payload = {
            "parameters": {
                "advertising_id": adid
            },
            "max_age": 0
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            return jsonify({"status": "error", "message": response.text}), response.status_code

        job = response.json().get("job")
        if not job:
            return jsonify({"status": "error", "message": "No job returned from Redash"}), 502

        job_id = job["id"]
        start = time.time()

        while True:
            response = requests.get(
                f"{REDASH_URL}/api/jobs/{job_id}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                return jsonify({"status": "error", "message": response.text}), response.status_code

            job = response.json()["job"]

            if job["status"] == 3:
                break

            if job["status"] == 4:
                return jsonify({"status": "error", "message": str(job)}), 502

            if time.time() - start > POLL_TIMEOUT:
                return jsonify({
                    "status": "error",
                    "message": f"Timed out waiting for Redash job {job_id}",
                }), 504

            time.sleep(POLL_INTERVAL)

        result_id = job["query_result_id"]
        response = requests.get(
            f"{REDASH_URL}/api/query_results/{result_id}",
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            return jsonify({"status": "error", "message": response.text}), response.status_code

        rows = response.json()["query_result"]["data"]["rows"]
        if not rows:
            return jsonify({"status": "empty"})

        return jsonify({"status": "success", "data": rows})

    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 502


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port)
