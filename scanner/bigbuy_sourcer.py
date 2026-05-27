"""
BigBuy sourcer — searches BigBuy's wholesale catalogue (EU/UK warehouse, ~350k products).

Credentials in .env:
  BIGBUY_API_KEY_PROD  — live environment (api.bigbuy.eu)
  BIGBUY_API_KEY_TEST  — sandbox environment (api.sandbox.bigbuy.eu)
  BIGBUY_USE_SANDBOX=True  — set this to use test env (default: False → prod)

API reference:
  Prod base : https://api.bigbuy.eu/rest/
  Test base : https://api.sandbox.bigbuy.eu/rest/
  Auth      : Authorization: Bearer {api_key}
  Search    : GET /catalog/search/products.json?term={term}&isoCode=en&lang=en
  Stock     : included in search response
  Pricing   : included in search response

Return shape matches AvasamSourcer (what pipeline expects):
  {
    "supplier":            "bigbuy",
    "supplier_product_id": str,
    "supplier_sku":        str,
    "wholesale_price":     float,
    "stock_count":         int,
    "supplier_title":      str,
    "supplier_image_url":  str,
  }
"""
import logging
from typing import Dict, List, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

BIGBUY_PROD_BASE = "https://api.bigbuy.eu/rest"
BIGBUY_TEST_BASE = "https://api.sandbox.bigbuy.eu/rest"


class BigBuySourcer:
    def __init__(self):
        if settings.bigbuy_use_sandbox:
            self._key = settings.bigbuy_api_key_test
            self._base = BIGBUY_TEST_BASE
        else:
            self._key = settings.bigbuy_api_key_prod
            self._base = BIGBUY_PROD_BASE

    @property
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._key}", "Accept": "application/json"}

    async def search(self, query: str, max_results: int = 10) -> Optional[Dict]:
        """
        Search BigBuy for a product matching `query`.
        Returns the best-priced in-stock match, or None if not found / key not set.
        """
        if not self._key:
            return None

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{self._base}/catalog/search/products.json",
                    headers=self._headers,
                    params={"term": query, "isoCode": "en", "lang": "en"},
                )
            if resp.status_code == 401:
                logger.error("BigBuy: invalid API key")
                return None
            if resp.status_code != 200:
                logger.warning("BigBuy search error %s for '%s'", resp.status_code, query)
                return None

            data = resp.json()
            products = data if isinstance(data, list) else data.get("products", [])

        except Exception as exc:
            logger.error("BigBuy search exception: %s", exc)
            return None

        return _best_match(products[:max_results], query)

    async def get_product(self, product_id: str) -> Optional[Dict]:
        """Fetch current price + stock for a known BigBuy product ID."""
        if not self._key:
            return None
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{self._base}/catalog/product/{product_id}.json",
                    headers=self._headers,
                )
            if resp.status_code != 200:
                return None
            return _parse_product(resp.json())
        except Exception as exc:
            logger.error("BigBuy get_product error: %s", exc)
            return None

    async def place_order(
        self,
        supplier_sku: str,
        quantity: int,
        recipient: Dict,
    ) -> Optional[str]:
        """
        Place a fulfilment order with BigBuy.
        recipient keys: name, address1, address2, city, state, postcode, country_code
        Returns the BigBuy order reference on success, None on failure.
        """
        if not self._key:
            return None
        payload = {
            "order": {
                "shippingAddress": {
                    "firstName": recipient.get("name", "").split()[0],
                    "lastName":  " ".join(recipient.get("name", "").split()[1:]) or "-",
                    "address":   recipient.get("address1", ""),
                    "postcode":  recipient.get("postcode", ""),
                    "town":      recipient.get("city", ""),
                    "province":  recipient.get("state", "") or recipient.get("city", ""),
                    "country":   recipient.get("country_code", "GB"),
                    "phone":     "00000000000",
                    "email":     settings.owner_email,
                },
                "products": [
                    {
                        "reference": supplier_sku,
                        "quantity":  quantity,
                        "internalReference": f"eBay-order",
                    }
                ],
            }
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(
                    f"{self._base}/order/create.json",
                    headers={**self._headers, "Content-Type": "application/json"},
                    json=payload,
                )
            if resp.status_code in (200, 201):
                data = resp.json()
                order_id = str(data.get("id") or data.get("order", {}).get("id", ""))
                logger.info("BigBuy: order placed — id=%s sku=%s", order_id, supplier_sku)
                return order_id
            logger.error("BigBuy place_order error %s: %s", resp.status_code, resp.text[:300])
            return None
        except Exception as exc:
            logger.error("BigBuy place_order exception: %s", exc)
            return None

    async def get_order_tracking(self, order_id: str) -> Optional[Dict]:
        """Poll BigBuy for tracking info on a submitted order."""
        if not self._key:
            return None
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{self._base}/order/{order_id}.json",
                    headers=self._headers,
                )
            if resp.status_code != 200:
                return None
            data = resp.json()
            shipments = data.get("order", data).get("shippings", [])
            if shipments:
                s = shipments[0]
                tracking = s.get("trackingNumber") or s.get("tracking_number")
                carrier = s.get("carrier") or s.get("shippingService", "")
                if tracking:
                    return {"tracking_number": tracking, "carrier": carrier}
            return None
        except Exception as exc:
            logger.error("BigBuy get_order_tracking error: %s", exc)
            return None


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_product(p: Dict) -> Optional[Dict]:
    """Normalise a BigBuy product dict to the standard supplier match shape."""
    price = float(
        p.get("wholesalePrice")
        or p.get("price")
        or p.get("cost")
        or 0
    )
    stock = int(p.get("stock") or p.get("stockAvailable") or p.get("quantity") or 0)
    if price <= 0 or stock <= 0:
        return None

    images = p.get("images") or []
    image_url = images[0].get("url", "") if images and isinstance(images[0], dict) else (
        images[0] if images else p.get("mainImage", "")
    )
    texts = p.get("texts") or p.get("descriptions") or []
    title = ""
    for t in texts:
        if isinstance(t, dict) and t.get("isoCode", "").startswith("en"):
            title = t.get("name") or t.get("title", "")
            break
    if not title:
        title = p.get("name") or p.get("title", "")

    return {
        "supplier":            "bigbuy",
        "supplier_product_id": str(p.get("id") or p.get("sku", "")),
        "supplier_sku":        str(p.get("sku") or p.get("reference", "")),
        "wholesale_price":     price,
        "stock_count":         stock,
        "supplier_title":      title,
        "supplier_image_url":  str(image_url),
    }


def _best_match(products: List[Dict], query: str) -> Optional[Dict]:
    """Return the lowest-priced in-stock product from a search results list."""
    parsed = [_parse_product(p) for p in products]
    valid = [p for p in parsed if p is not None]
    if not valid:
        return None
    return min(valid, key=lambda p: p["wholesale_price"])
