"""
Fetch eBay account policies and save IDs to .env.
Run once after setup_ebay_auth.py.
Usage: python get_ebay_policies.py
"""
import httpx
from dotenv import set_key
from config.settings import settings

BASE = "https://api.ebay.com/sell/account/v1"
MKT  = "EBAY_GB"


def _headers():
    return {"Authorization": f"Bearer {settings.ebay_access_token}"}


def fetch(endpoint: str) -> dict:
    resp = httpx.get(f"{BASE}/{endpoint}?marketplace_id={MKT}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def pick(policies: list, label: str) -> str:
    if not policies:
        return ""
    if len(policies) == 1:
        return policies[0]["policyId"] if "policyId" in policies[0] else policies[0].get("fulfillmentPolicyId") or policies[0].get("paymentPolicyId") or policies[0].get("returnPolicyId") or ""
    print(f"\n{label} — multiple found, pick one:")
    for i, p in enumerate(policies):
        pid = p.get("policyId") or p.get("fulfillmentPolicyId") or p.get("paymentPolicyId") or p.get("returnPolicyId")
        print(f"  [{i}] {p.get('name', 'unnamed')} — {pid}")
    idx = int(input("Enter number: ").strip())
    p = policies[idx]
    return p.get("policyId") or p.get("fulfillmentPolicyId") or p.get("paymentPolicyId") or p.get("returnPolicyId") or ""


def main():
    print("Fetching eBay account policies for EBAY_GB...")

    try:
        fp = fetch("fulfillment_policy")
        fulfillment_id = pick(fp.get("fulfillmentPolicies", []), "Fulfillment policies")
        set_key(".env", "EBAY_FULFILLMENT_POLICY_ID", fulfillment_id)
        print(f"EBAY_FULFILLMENT_POLICY_ID = {fulfillment_id}")
    except Exception as e:
        print(f"Fulfillment policy fetch failed: {e}")

    try:
        pp = fetch("payment_policy")
        payment_id = pick(pp.get("paymentPolicies", []), "Payment policies")
        set_key(".env", "EBAY_PAYMENT_POLICY_ID", payment_id)
        print(f"EBAY_PAYMENT_POLICY_ID     = {payment_id}")
    except Exception as e:
        print(f"Payment policy fetch failed: {e}")

    try:
        rp = fetch("return_policy")
        return_id = pick(rp.get("returnPolicies", []), "Return policies")
        set_key(".env", "EBAY_RETURN_POLICY_ID", return_id)
        print(f"EBAY_RETURN_POLICY_ID      = {return_id}")
    except Exception as e:
        print(f"Return policy fetch failed: {e}")

    print("\nDone — policies saved to .env")


if __name__ == "__main__":
    main()
