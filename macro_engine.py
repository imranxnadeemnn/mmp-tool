import uuid
from appsflyer_sign import sign_tracking_url
from config import ANDROID_BUNDLE, IOS_BUNDLE


def apply_macros(url, platform):
    """
    Replace ONLY:
    - {bundle_id}
    - {click_id}
    """

    if not url:
        return url

    # ------------------------------
    # STEP 1: Bundle ID
    # ------------------------------
    if platform.lower() == "ios":
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
    # STEP 3: Apply AppsFlyer signing
    # ------------------------------
    url = sign_tracking_url(url)

    return url