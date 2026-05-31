"""
eBay OAuth setup — run once to get access + refresh tokens.
Usage: python setup_ebay_auth.py
"""
import base64
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import os
import httpx
from dotenv import load_dotenv, set_key

load_dotenv()
APP_ID  = os.getenv("EBAY_APP_ID", "")
CERT_ID = os.getenv("EBAY_CERT_ID", "")
RUNAME  = os.getenv("EBAY_RUNAME", "Nick_Cox-NickCox-NickPri-bzvqjfl")
PORT    = 8080

SCOPES = " ".join([
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
])

AUTH_URL  = "https://auth.ebay.com/oauth2/authorize"
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"

auth_code: str | None = None
done = threading.Event()


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        qs = parse_qs(urlparse(self.path).query)
        code = qs.get("code", [None])[0]
        if code:
            auth_code = code
            body = b"<h1>Authorisation complete &#8212; you can close this tab.</h1>"
            self.send_response(200)
        else:
            body = b"<h1>No code received.</h1>"
            self.send_response(400)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)
        done.set()

    def log_message(self, *_):
        pass


def main():
    server = HTTPServer(("localhost", PORT), _Handler)
    threading.Thread(target=server.handle_request, daemon=True).start()

    url = AUTH_URL + "?" + urlencode({
        "client_id": APP_ID,
        "redirect_uri": RUNAME,
        "response_type": "code",
        "scope": SCOPES,
    })

    print("Opening browser — sign in with your eBay seller account (cox333)...")
    webbrowser.open(url)

    if not done.wait(timeout=120):
        print("Timed out — no response received within 2 minutes.")
        return

    if not auth_code:
        print("No authorisation code received.")
        return

    creds = base64.b64encode(f"{APP_ID}:{CERT_ID}".encode()).decode()
    resp = httpx.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": RUNAME,
        },
    )

    data = resp.json()
    if "access_token" not in data:
        print(f"Token exchange failed:\n{data}")
        return

    set_key(".env", "EBAY_ACCESS_TOKEN", data["access_token"])
    refresh = data.get("refresh_token", "")
    if refresh:
        set_key(".env", "EBAY_REFRESH_TOKEN", refresh)

    print("\nTokens saved to .env")
    print(f"Access token expires in {data.get('expires_in', '?')}s (~2 hours)")
    if refresh:
        print(f"Refresh token expires in {data.get('refresh_token_expires_in', '?')}s (~18 months)")


if __name__ == "__main__":
    main()
