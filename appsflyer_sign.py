import time
import uuid
import jwt
from urllib.parse import urlparse, parse_qs


# 🔐 Replace with your real S2S token
AF_S2S_TOKEN = "9002b474-e5cb-4f73-a305-15b62bf95bda"


def extract_params_from_url(url):
    """
    Extract query params from URL into a flat dict
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    params = {}

    for k, v in query.items():
        params[k] = v[0] if isinstance(v, list) else v

    return params


def get_app_id_from_url(url):
    """
    Extract app id from URL path
    Example:
    https://app.appsflyer.com/id123456789 → id123456789
    """
    parsed = urlparse(url)
    return parsed.path.strip("/")


def build_payload(params, app_id):
    """
    Build JWT payload as per AppsFlyer C2S spec
    """

    now = int(time.time())

    payload = {
        "iss": params.get("pid"),                 # media source
        "aud": ["click"],                         # click API
        "ver": "v1",
        "iat": now,
        "exp": now + 300,                         # 5 min TTL
        "jti": params.get("clickid", str(uuid.uuid4())),
        "sub": app_id,
        "params": {}
    }

    # 🔥 IMPORTANT: Only include authoritative params IF present in URL
    allowed_params = [
        "pid",
        "c",
        "af_siteid",
        "af_sub1", "af_sub2", "af_sub3", "af_sub4", "af_sub5",
        "af_ip",
        "af_ua",
        "advertising_id",
        "idfa",
        "android_id",
        "idfv",
        "gclid",
        "fbclid",
        "ttclid"
    ]

    for key in allowed_params:
        if key in params:
            payload["params"][key] = params[key]

    return payload


def sign_tracking_url(url):
    """
    Main function to generate af_sig and append to URL
    """

    # ❌ Remove old params if present
    url = remove_old_signature_params(url)

    params = extract_params_from_url(url)
    app_id = get_app_id_from_url(url)

    payload = build_payload(params, app_id)

    token = jwt.encode(payload, AF_S2S_TOKEN, algorithm="HS256")

    # Append af_sig
    separator = "&" if "?" in url else "?"
    signed_url = f"{url}{separator}af_sig={token}"

    return signed_url


def remove_old_signature_params(url):
    """
    Remove old AppsFlyer signing params (VERY IMPORTANT)
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Remove old fields
    query.pop("signature", None)
    query.pop("expires", None)
    query.pop("af_sig", None)

    # rebuild query
    new_query = "&".join([f"{k}={v[0]}" for k, v in query.items()])

    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    return f"{base_url}?{new_query}" if new_query else base_url