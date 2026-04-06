import os


AF_DEV_KEY = os.getenv("AF_DEV_KEY", "DEV_KEY")
AF_SECRET = os.getenv("AF_SECRET", "SECRET")

# Redash
REDASH_URL = os.getenv("REDASH_URL", "https://redash.aarki.org").rstrip("/")
API_KEY = os.getenv("REDASH_API_KEY", os.getenv("API_KEY", ""))
QUERY_ID = int(os.getenv("REDASH_QUERY_ID", "28702"))
REDASH_REQUEST_TIMEOUT = int(os.getenv("REDASH_REQUEST_TIMEOUT", "10"))
REDASH_POLL_TIMEOUT = int(os.getenv("REDASH_POLL_TIMEOUT", "20"))
REDASH_POLL_INTERVAL = float(os.getenv("REDASH_POLL_INTERVAL", "1"))
RESULT_PROXY_URL = os.getenv("RESULT_PROXY_URL", "").rstrip("/")
RESULT_PROXY_TOKEN = os.getenv("RESULT_PROXY_TOKEN", "")
RESULT_PROXY_TIMEOUT = int(os.getenv("RESULT_PROXY_TIMEOUT", "30"))
RESULT_VIEWER_URL = os.getenv("RESULT_VIEWER_URL", "http://localhost:8501")

# ClickHouse (future use)
CH_HOST = os.getenv("CH_HOST", "localhost")
CH_PORT = int(os.getenv("CH_PORT", "8123"))
CH_USER = os.getenv("CH_USER", "default")
CH_PASS = os.getenv("CH_PASS", "")
CH_DB = os.getenv("CH_DB", "post")

ANDROID_BUNDLE = os.getenv("ANDROID_BUNDLE", "com.mmp.testtool")
IOS_BUNDLE = os.getenv("IOS_BUNDLE", "com.mmp.testtool.ios")
