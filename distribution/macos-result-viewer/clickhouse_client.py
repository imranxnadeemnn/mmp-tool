import time

import pandas as pd
import requests
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


def _run_query():
    """
    Trigger a fresh run of the configured Redash query (no parameters) and
    return the result rows. The query itself owns all filtering
    (SE_ app filter + last-7-days window), so the client just fetches results.
    """
    if not API_KEY:
        raise Exception("REDASH_API_KEY is not configured")

    url = f"{REDASH_URL}/api/queries/{QUERY_ID}/results"
    payload = {"max_age": 0}

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

        if status == 3:
            break

        if status == 4:
            raise Exception(f"Query failed: {job}")

        if time.time() - start > REDASH_POLL_TIMEOUT:
            raise Exception(
                f"Timed out waiting for Redash job {job_id} "
                f"after {REDASH_POLL_TIMEOUT}s"
            )

        time.sleep(REDASH_POLL_INTERVAL)

    result_id = job.get("query_result_id")
    if not result_id:
        raise Exception(f"Job {job_id} finished without query_result_id")

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

    return r.json()["query_result"]["data"]["rows"]


def get_results():
    """Return the latest test postbacks as a DataFrame."""
    rows = _run_query()
    return pd.DataFrame(rows)


def check_redash_connection():
    """Lightweight health check used by the /debug/redash endpoint."""
    try:
        rows = _run_query()
    except Exception as exc:
        return {
            "ok": False,
            "message": str(exc),
        }

    return {
        "ok": True,
        "message": "Redash query completed successfully",
        "row_count": len(rows),
    }
