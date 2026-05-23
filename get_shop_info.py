"""
Run after setup_etsy_auth.py to get your ETSY_SHOP_ID and ETSY_SHIPPING_PROFILE_ID.
These go in your .env file.

Usage:
  python get_shop_info.py
"""
import os
import httpx
from dotenv import load_dotenv, set_key

load_dotenv()

API_KEY = os.getenv("ETSY_API_KEY", "")
API_SECRET = os.getenv("ETSY_API_SECRET", "")
ACCESS_TOKEN = os.getenv("ETSY_ACCESS_TOKEN", "")
HEADERS = {
    "x-api-key": f"{API_KEY}:{API_SECRET}",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}
BASE = "https://openapi.etsy.com/v3"


def main():
    if not ACCESS_TOKEN:
        print("ERROR: Run setup_etsy_auth.py first to get ETSY_ACCESS_TOKEN")
        return

    # 1. Get user info
    r = httpx.get(f"{BASE}/application/users/me", headers=HEADERS)
    if r.status_code != 200:
        print(f"ERROR: Could not fetch user info: {r.status_code} {r.text}")
        return
    user_id = r.json()["user_id"]
    print(f"User ID: {user_id}")

    # 2. Get shop
    r = httpx.get(f"{BASE}/application/users/{user_id}/shops", headers=HEADERS)
    if r.status_code != 200:
        print(f"ERROR: Could not fetch shop: {r.status_code} {r.text}")
        return
    shop = r.json()
    shop_id = str(shop["shop_id"])
    shop_name = shop["shop_name"]
    print(f"Shop: {shop_name}  (ID: {shop_id})")
    set_key(".env", "ETSY_SHOP_ID", shop_id)
    print(f"ETSY_SHOP_ID={shop_id} saved to .env")

    # 3. Get shipping profiles
    r = httpx.get(f"{BASE}/application/shops/{shop_id}/shipping-profiles", headers=HEADERS)
    if r.status_code != 200:
        print(f"\nWARNING: Could not fetch shipping profiles: {r.status_code}")
        print("Create a shipping profile in your Etsy shop settings first, then re-run this script.")
        return

    profiles = r.json().get("results", [])
    if not profiles:
        print("\nNo shipping profiles found.")
        print("Go to Etsy Shop Manager → Settings → Shipping settings → Add a shipping profile.")
        print("Then re-run this script.")
        return

    print(f"\nShipping profiles:")
    for p in profiles:
        print(f"  ID: {p['shipping_profile_id']}  Name: {p['title']}")

    if len(profiles) == 1:
        profile_id = str(profiles[0]["shipping_profile_id"])
        set_key(".env", "ETSY_SHIPPING_PROFILE_ID", profile_id)
        print(f"\nETSY_SHIPPING_PROFILE_ID={profile_id} saved to .env (only one profile found)")
    else:
        print("\nMultiple profiles found — add the correct ID to .env manually:")
        print("  ETSY_SHIPPING_PROFILE_ID=<id from above>")


if __name__ == "__main__":
    main()
