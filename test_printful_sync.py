"""
Quick test: create a Printful sync product and see if it appears on the connected Etsy store.
Uses a public test image — no AI generation needed.
Run: python test_printful_sync.py
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

PRINTFUL_API = "https://api.printful.com"
API_KEY = os.getenv("PRINTFUL_API_KEY", "")
STORE_ID = os.getenv("PRINTFUL_STORE_ID", "")

# Public domain test image (simple coloured square — valid for Printful upload test)
TEST_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-PF-Store-Id": STORE_ID,
}


async def get_stores():
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{PRINTFUL_API}/stores") as resp:
            data = await resp.json()
            print("\n--- Stores on this account ---")
            for s in data.get("result", []):
                print(f"  id={s['id']}  name={s['name']}  type={s['type']}  status={s.get('status', '?')}")
            return data.get("result", [])


async def create_test_product():
    payload = {
        "sync_product": {
            "name": "[TEST] POD Bot Sync Check — delete me",
            "description": "Automated test product — safe to delete",
        },
        "sync_variants": [
            {
                "variant_id": 4012,  # Bella+Canvas 3001 Small White
                "retail_price": "25.00",
                "files": [
                    {
                        "type": "front",
                        "url": TEST_IMAGE_URL,
                    }
                ],
            }
        ],
    }

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(f"{PRINTFUL_API}/store/products", json=payload) as resp:
            data = await resp.json()
            print("\n--- Create sync product response ---")
            if data.get("code") == 200:
                result = data["result"]
                product_id = result.get("id")
                etsy_id = result.get("external_id")
                print(f"  Printful product ID : {product_id}")
                print(f"  External (Etsy) ID  : {etsy_id}")
                print(f"  Name                : {result.get('name')}")
                syncs = result.get("sync_variants", [])
                for v in syncs:
                    print(f"  Variant sync status : {v.get('status')}  external_id={v.get('external_id')}")
                if etsy_id:
                    print("\n  RESULT: Etsy listing ID received — Printful sync IS pushing to Etsy.")
                else:
                    print("\n  RESULT: No external_id returned — product created in Printful only.")
                    print("  This may mean the store connection needs checking, or sync is async.")
                return product_id
            else:
                print(f"  ERROR: code={data.get('code')}  error={data.get('error')}")
                print(f"  Full response: {data}")
                return None


async def check_product(product_id: int):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(f"{PRINTFUL_API}/store/products/{product_id}") as resp:
            data = await resp.json()
            result = data.get("result", {})
            product = result.get("sync_product", {})
            variants = result.get("sync_variants", [])
            print(f"\n--- Product check (id={product_id}) ---")
            print(f"  Name        : {product.get('name')}")
            print(f"  External ID : {product.get('external_id')}")
            print(f"  Status      : {product.get('status')}")
            for v in variants:
                print(f"  Variant {v.get('id')} status={v.get('status')} external_id={v.get('external_id')}")


async def main():
    if not API_KEY:
        print("ERROR: PRINTFUL_API_KEY not found in .env")
        return
    if not STORE_ID:
        print("WARNING: PRINTFUL_STORE_ID not set — using default store for this API key")

    print(f"API key loaded: {API_KEY[:8]}...")
    print(f"Store ID      : {STORE_ID or '(not set)'}")

    stores = await get_stores()

    product_id = await create_test_product()

    if product_id:
        # Give Printful a moment to process the sync
        print("\nWaiting 5 seconds for Printful to process...")
        await asyncio.sleep(5)
        await check_product(product_id)
        print(f"\nCheck your Etsy shop (NickPrintCo) for a draft listing called '[TEST] POD Bot Sync Check'")
        print(f"Also check: https://www.printful.com/dashboard/store — product ID {product_id}")


if __name__ == "__main__":
    asyncio.run(main())
