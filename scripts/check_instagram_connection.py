"""Read-only check for Instagram Login API credentials."""
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def check_connection(access_token, api_version="v25.0", opener=urlopen):
    if not access_token or not access_token.strip():
        raise ValueError("Missing INSTAGRAM_ACCESS_TOKEN secret.")
    version = api_version.strip()
    if not version.startswith("v") or not version[1:].replace(".", "").isdigit():
        raise ValueError("INSTAGRAM_API_VERSION must look like v25.0.")
    url = f"https://graph.instagram.com/{version}/me?{urlencode({'fields': 'user_id,username', 'access_token': access_token})}"
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with opener(request, timeout=20) as response:
            status = getattr(response, "status", 200)
            body = response.read().decode("utf-8")
    except HTTPError as error:
        # Do not print response URLs or request details, which can contain the token.
        raise RuntimeError(f"Instagram API returned HTTP {error.code}. Check token, permissions, and API version.") from None
    except URLError as error:
        raise RuntimeError(f"Could not reach Instagram API ({error.reason.__class__.__name__}).") from None
    if status < 200 or status >= 300:
        raise RuntimeError(f"Instagram API returned HTTP {status}.")
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError("Instagram API returned an unreadable response.") from None
    if not isinstance(data, dict) or not data.get("username") or not (data.get("user_id") or data.get("id")):
        # Never display the full response because it may contain sensitive details.
        raise RuntimeError("API response did not include account ID and username. Verify the Instagram Login token and permissions.")
    return {"user_id": str(data.get("user_id") or data.get("id")), "username": str(data["username"])}


def main():
    token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
    version = os.environ.get("INSTAGRAM_API_VERSION", "v25.0")
    try:
        account = check_connection(token, version)
    except (ValueError, RuntimeError) as error:
        print("Instagram connection check failed: " + str(error))
        raise SystemExit(1)
    print("Instagram Login API connection successful (read-only).")
    print("Username: @" + account["username"])
    print("Account ID: " + account["user_id"])
    print("No posts were created or published.")


if __name__ == "__main__":
    main()
