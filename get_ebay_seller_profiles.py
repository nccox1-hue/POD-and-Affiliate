"""
Fetch eBay seller business policy IDs via Trading API (Auth'n'Auth).
Run once to find your shipping/payment/return policy IDs.
Usage: python get_ebay_seller_profiles.py
"""
import re
import httpx
from dotenv import set_key
from config.settings import settings

TRADING_API = "https://api.ebay.com/ws/api.dll"

HEADERS = {
    "X-EBAY-API-COMPATIBILITY-LEVEL": "1155",
    "X-EBAY-API-SITEID": "3",
    "X-EBAY-API-CALL-NAME": "GetUserPreferences",
    "X-EBAY-API-APP-NAME":  settings.ebay_app_id,
    "X-EBAY-API-DEV-NAME":  settings.ebay_dev_id,
    "X-EBAY-API-CERT-NAME": settings.ebay_cert_id,
    "X-EBAY-API-IAFTOKEN":  settings.ebay_access_token,
    "Content-Type": "text/xml",
}

XML = f"""<?xml version="1.0" encoding="utf-8"?>
<GetUserPreferencesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{settings.ebay_access_token}</eBayAuthToken>
  </RequesterCredentials>
  <ShowSellerProfilePreferences>true</ShowSellerProfilePreferences>
</GetUserPreferencesRequest>"""


def extract_all(tag: str, text: str) -> list[str]:
    return re.findall(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)


def main():
    resp = httpx.post(TRADING_API, content=XML.encode(), headers=HEADERS)
    body = resp.text

    if "<Ack>Failure</Ack>" in body:
        errors = re.findall(r"<LongMessage>(.*?)</LongMessage>", body)
        print("API call failed:", "; ".join(errors))
        print(body[:1000])
        return

    # Extract profile blocks
    profiles = re.findall(
        r"<SupportedSellerProfile>(.*?)</SupportedSellerProfile>", body, re.DOTALL
    )

    if not profiles:
        print("No seller profiles found in response.")
        print(body[:2000])
        return

    shipping, payment, returns = [], [], []

    for p in profiles:
        pid   = (re.findall(r"<ProfileID>(\d+)</ProfileID>", p) or ["?"])[0]
        pname = (re.findall(r"<ProfileName>(.*?)</ProfileName>", p) or ["?"])[0]
        ptype = (re.findall(r"<ProfileType>(.*?)</ProfileType>", p) or ["?"])[0]
        entry = (pid, pname)
        if "SHIPPING" in ptype.upper():
            shipping.append(entry)
        elif "PAYMENT" in ptype.upper():
            payment.append(entry)
        elif "RETURN" in ptype.upper():
            returns.append(entry)

    def pick(items: list, label: str) -> str:
        if not items:
            print(f"No {label} profiles found.")
            return ""
        if len(items) == 1:
            pid, pname = items[0]
            print(f"{label}: {pname} ({pid})")
            return pid
        print(f"\n{label} profiles:")
        for i, (pid, pname) in enumerate(items):
            print(f"  [{i}] {pname} — {pid}")
        idx = int(input("Pick number: ").strip())
        return items[idx][0]

    print("\n--- eBay Business Policies ---")
    shipping_id = pick(shipping, "Shipping")
    payment_id  = pick(payment,  "Payment")
    return_id   = pick(returns,  "Return")

    if shipping_id:
        set_key(".env", "EBAY_SHIPPING_POLICY_ID", shipping_id)
    if payment_id:
        set_key(".env", "EBAY_PAYMENT_POLICY_ID", payment_id)
    if return_id:
        set_key(".env", "EBAY_RETURN_POLICY_ID", return_id)

    print("\nPolicy IDs saved to .env")


if __name__ == "__main__":
    main()
