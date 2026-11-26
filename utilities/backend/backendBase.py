import os

import requests
from dotenv import load_dotenv

load_dotenv()

__all__ = ["table", "rpc"]


URL = "https://vtimmqlnyoyxiwczfdwf.supabase.co"
ANON_KEY = os.environ["SUPABASE_ANON_KEY"]  # publishable key only
EMAIL = os.environ["TEST_USER_EMAIL"]
PASSWORD = os.environ["TEST_USER_PASSWORD"]

def signIn(email, password):
    r = requests.post(
        f"{URL}/auth/v1/token?grant_type=password",
        headers={"apikey": ANON_KEY},
        json={"email": email, "password": password},
    )
    r.raise_for_status()
    return r.json()  # access_token, refresh_token, expires_in

def rpc(fn, params=None):    
    session = signIn(EMAIL, PASSWORD)
    token = session.get("access_token")
    r = requests.post(
        f"{URL}/rest/v1/rpc/{fn}",
        headers={"apikey": ANON_KEY, "Authorization": f"Bearer {token}"},
        json=params or {},
    )
    if not r.ok:
        raise RuntimeError(f"{fn}: {r.status_code} {r.text}")
    return r.json()

def table(tableName, params = None):
    session = signIn(EMAIL, PASSWORD)
    token = session.get("access_token")
    tableData = requests.get(
        f"{URL}/rest/v1/{tableName}",
        headers={"apikey": ANON_KEY, "Authorization": f"Bearer {token}"},
        params=params,
    )
    tableData.raise_for_status()
    return tableData