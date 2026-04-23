import uuid
from urllib.parse import urlparse

from appsflyer_sign import sign_tracking_url
from config import ANDROID_BUNDLE, IOS_BUNDLE


def should_sign_with_appsflyer(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    return "appsflyer.com" in host


def apply_macros(url, platform):
    """
    Replace supported local macros:
    - {bundle_id}
    - {click_id}
    - {campaign_name}
    - {creative_name}
    """

    if not url:
        return url

    normalized_platform = (platform or "").strip()

    # ------------------------------
    # STEP 1: Bundle ID
    # ------------------------------
    if normalized_platform.lower() == "ios":
        bundle_id = IOS_BUNDLE
    else:
        bundle_id = ANDROID_BUNDLE

    url = url.replace("{bundle_id}", bundle_id)

    # ------------------------------
    # STEP 2: Click ID
    # ------------------------------
    click_id = str(uuid.uuid4())
    url = url.replace("{click_id}", click_id)

    # ------------------------------
    # STEP 3: Campaign/Creative names
    # ------------------------------
    campaign_name = f"campaign_{uuid.uuid4().hex[:10]}"
    creative_name = f"creative_{uuid.uuid4().hex[:10]}"
    url = url.replace("{campaign_name}", campaign_name)
    url = url.replace("{creative_name}", creative_name)

    # ------------------------------
    # STEP 4: Apply AppsFlyer signing only for AppsFlyer links
    # ------------------------------
    if should_sign_with_appsflyer(url):
        url = sign_tracking_url(url)

    return url
