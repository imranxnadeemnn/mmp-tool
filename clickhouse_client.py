import requests
import time
import pandas as pd
from config import REDASH_URL, API_KEY, QUERY_ID

headers = {
    "Authorization": f"Key {API_KEY}"
}


def get_result(adid):

    print("🔍 Querying Redash for:", adid)

    url = f"{REDASH_URL}/api/queries/{QUERY_ID}/results"

    payload = {
        "parameters": {
            "advertising_id": adid
        },
        "max_age": 0
    }

    r = requests.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        raise Exception(f"POST failed: {r.text}")

    job = r.json().get("job")

    if not job:
        raise Exception("No job returned from Redash")

    job_id = job["id"]

    print("🧠 Job ID:", job_id)

    # ✅ TIMEOUT SAFE POLLING
    MAX_WAIT = 15
    start = time.time()

    while True:

        r = requests.get(
            f"{REDASH_URL}/api/jobs/{job_id}",
            headers=headers,
        )

        job = r.json()["job"]
        status = job["status"]

        print("⏳ Job status:", status)

        if status == 3:
            break

        if status == 4:
            raise Exception(f"Query failed: {job}")

        if time.time() - start > MAX_WAIT:
            print("⚠️ Timeout reached")
            return None

        time.sleep(1)

    result_id = job["query_result_id"]

    r = requests.get(
        f"{REDASH_URL}/api/query_results/{result_id}",
        headers=headers,
    )

    data = r.json()
    rows = data["query_result"]["data"]["rows"]

    print("✅ Rows fetched:", len(rows))

    return pd.DataFrame(rows)