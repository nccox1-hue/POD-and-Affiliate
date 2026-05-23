"""
Run this once to get your Etsy OAuth access token.
Saves the token to .env automatically.

Usage:
  python setup_etsy_auth.py

Requires ETSY_API_KEY and ETSY_API_SECRET in .env first.
Get them at: https://www.etsy.com/developers/register
"""
import os
import hashlib
import base64
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import httpx
from dotenv import load_dotenv, set_key

load_dotenv()

API_KEY = os.getenv("ETSY_API_KEY", "")
API_SECRET = os.getenv("ETSY_API_SECRET", "")
REDIRECT_URI = "http://localhost:3003/callback"
SCOPES = "listings_w listings_r shops_r transactions_r"

auth_code = None


def pkce_pair():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = parse_qs(urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Etsy authorised! You can close this tab.</h2>")

    def log_message(self, *args):
        pass


def main():
    if not API_KEY:
        print("ERROR: Set ETSY_API_KEY in .env first")
        return

    verifier, challenge = pkce_pair()
    state = secrets.token_hex(8)

    auth_url = (
        f"https://www.etsy.com/oauth/connect"
        f"?response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES.replace(' ', '%20')}"
        f"&client_id={API_KEY}"
        f"&state={state}"
        f"&code_challenge={challenge}"
        f"&code_challenge_method=S256"
    )

    print(f"\nOpening Etsy authorisation page...\n{auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 3003), CallbackHandler)
    server.handle_request()

    if not auth_code:
        print("ERROR: No auth code received")
        return

    # Exchange code for token
    resp = httpx.post(
        "https://api.etsy.com/v3/public/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": auth_code,
            "code_verifier": verifier,
        },
    )
    data = resp.json()

    if "access_token" not in data:
        print(f"ERROR: Token exchange failed: {data}")
        return

    set_key(".env", "ETSY_ACCESS_TOKEN", data["access_token"])
    if data.get("refresh_token"):
        set_key(".env", "ETSY_REFRESH_TOKEN", data["refresh_token"])
    print(f"\nEtsy tokens saved to .env")
    print(f"  Access token expires in: {data.get('expires_in', '?')}s (1 hour)")
    print(f"  Refresh token saved: {'yes' if data.get('refresh_token') else 'no'}")
    print(f"\nNext: run python get_shop_info.py to get your ETSY_SHOP_ID and shipping profile ID")


if __name__ == "__main__":
    main()
