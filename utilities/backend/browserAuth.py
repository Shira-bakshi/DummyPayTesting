import json
import time
from urllib.parse import urlsplit

from playwright.sync_api import StorageState

from utilities.backend.backendBase import EMAIL, PASSWORD, URL, signIn
from utilities.consts import FILE_PATH


def createAuthStorageState() -> StorageState:
    session = signIn(EMAIL, PASSWORD)
    if "expires_at" not in session:
        session["expires_at"] = int(time.time()) + session["expires_in"]

    appUrl = urlsplit(FILE_PATH)
    projectRef = urlsplit(URL).hostname.split(".", 1)[0]
    return {
        "cookies": [],
        "origins": [
            {
                "origin": f"{appUrl.scheme}://{appUrl.netloc}",
                "localStorage": [
                    {"name": f"sb-{projectRef}-auth-token", "value": json.dumps(session)}
                ],
            }
        ],
    }
