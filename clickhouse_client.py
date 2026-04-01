import requests
import time
import pandas as pd
from requests import RequestException

from config import (
    API_KEY,
    QUERY_ID,
    REDASH_POLL_INTERVAL,
    REDASH_POLL_TIMEOUT,
    REDASH_REQUEST_TIMEOUT,
    REDASH_URL,
)

headers = {
    "Authorization": f"Key {API_KEY}"
}


def check_redash_connection(adid):
    if not API_KEY:
        return {
            "ok": False,
            "step": "config",
            "message": "REDASH_API_KEY is not configured",
        }

    url = f"{REDASH_URL}/api/queries/{QUERY_ID}/results"
    payload = {
        "parameters": {
            "advertising_id": adid
        },
        "max_age": 0
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=REDASH_REQUEST_TIMEOUT,
        )
    except RequestException as exc:
        return {
            "ok": False,
            "step": "post",
            "message": f"Unable to reach Redash POST endpoint: {exc}",
        }

    if r.status_code != 200:
        return {
            "ok": False,
            "step": "post",
            "message": f"POST failed: {r.text}",
            "status_code": r.status_code,
        }

    job = r.json().get("job")
    if not job:
        return {
            "ok": False,
            "step": "post",
            "message": "No job returned from Redash",
        }

    job_id = job["id"]
    start = time.time()

    while True:
        try:
            r = requests.get(
                f"{REDASH_URL}/api/jobs/{job_id}",
                headers=headers,
                timeout=REDASH_REQUEST_TIMEOUT,
            )
        except RequestException as exc:
            return {
                "ok": False,
                "step": "poll",
                "message": f"Unable to poll Redash job {job_id}: {exc}",
                "job_id": job_id,
            }

        if r.status_code != 200:
            return {
                "ok": False,
                "step": "poll",
                "message": f"Job poll failed: {r.text}",
                "job_id": job_id,
                "status_code": r.status_code,
            }

        job = r.json()["job"]
        status = job["status"]

        if status == 3:
            break

        if status == 4:
            return {
                "ok": False,
                "step": "poll",
                "message": f"Query failed: {job}",
                "job_id": job_id,
            }

        if time.time() - start > REDASH_POLL_TIMEOUT:
            return {
                "ok": False,
                "step": "poll",
                "message": (
                    f"Timed out waiting for Redash job {job_id} "
                    f"after {REDASH_POLL_TIMEOUT}s"
                ),
                "job_id": job_id,
            }

        time.sleep(REDASH_POLL_INTERVAL)

    result_id = job.get("query_result_id")
    if not result_id:
        return {
            "ok": False,
            "step": "result",
            "message": f"Job {job_id} finished without query_result_id",
            "job_id": job_id,
        }

    try:
        r = requests.get(
            f"{REDASH_URL}/api/query_results/{result_id}",
            headers=headers,
            timeout=REDASH_REQUEST_TIMEOUT,
        )
    except RequestException as exc:
        return {
            "ok": False,
            "step": "result",
            "message": f"Unable to fetch Redash result set {result_id}: {exc}",
            "job_id": job_id,
            "result_id": result_id,
        }

    if r.status_code != 200:
        return {
            "ok": False,
            "step": "result",
            "message": f"Result fetch failed: {r.text}",
            "job_id": job_id,
            "result_id": result_id,
            "status_code": r.status_code,
        }

    rows = r.json()["query_result"]["data"]["rows"]
    return {
        "ok": True,
        "step": "result",
        "message": "Redash query completed successfully",
        "job_id": job_id,
        "result_id": result_id,
        "row_count": len(rows),
    }


def get_result(adid):
    if not API_KEY:
        raise Exception("REDASH_API_KEY is not configured")

    print("🔍 Querying Redash for:", adid)

    url = f"{REDASH_URL}/api/queries/{QUERY_ID}/results"

    payload = {
        "parameters": {
            "advertising_id": adid
        },
        "max_age": 0
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=REDASH_REQUEST_TIMEOUT,
        )
    except RequestException as exc:
        raise Exception(f"Unable to reach Redash POST endpoint: {exc}") from exc

    if r.status_code != 200:
        raise Exception(f"POST failed: {r.text}")

    job = r.json().get("job")

    if not job:
        raise Exception("No job returned from Redash")

    job_id = job["id"]

    print("🧠 Job ID:", job_id)

    # ✅ TIMEOUT SAFE POLLING
    MAX_WAIT = REDASH_POLL_TIMEOUT
    start = time.time()

    while True:
        try:
            r = requests.get(
                f"{REDASH_URL}/api/jobs/{job_id}",
                headers=headers,
                timeout=REDASH_REQUEST_TIMEOUT,
            )
        except RequestException as exc:
            raise Exception(f"Unable to poll Redash job {job_id}: {exc}") from exc

        job = r.json()["job"]
        status = job["status"]

        print("⏳ Job status:", status)

        if status == 3:
            break

        if status == 4:
            raise Exception(f"Query failed: {job}")

        if time.time() - start > MAX_WAIT:
            raise Exception(
                f"Timed out waiting for Redash job {job_id} after {MAX_WAIT}s"
            )

        time.sleep(REDASH_POLL_INTERVAL)

    result_id = job["query_result_id"]

    try:
        r = requests.get(
            f"{REDASH_URL}/api/query_results/{result_id}",
            headers=headers,
            timeout=REDASH_REQUEST_TIMEOUT,
        )
    except RequestException as exc:
        raise Exception(
            f"Unable to fetch Redash result set {result_id}: {exc}"
        ) from exc

    if r.status_code != 200:
        raise Exception(f"Result fetch failed: {r.text}")

    data = r.json()
    rows = data["query_result"]["data"]["rows"]

    print("✅ Rows fetched:", len(rows))

    return pd.DataFrame(rows)
