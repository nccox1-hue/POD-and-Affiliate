"""
Avasam Seller API client.

Auth: POST consumer_key + secret_key → access_token (cached, re-fetched on expiry).
Credentials: Settings → User Management → API Keys in Avasam dashboard.

Product search: Avasam has no free-text search endpoint. Products are fetched via
GetInventoryListWithFilter with optional CategoryName filter, then matched locally
by title word overlap.

API base: https://app.avasam.com
Docs: https://help.avasam.com/docs/seller-api
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

BASE = "https://app.avasam.com"
AUTH_URL = f"{BASE}/api/auth/request-token"
PRODUCT_LIST_URL = f"{BASE}/apiseeker/Products/GetSellerProductList"
INVENTORY_FILTER_URL = f"{BASE}/apiseeker/ProductModule/GetInventoryListWithFilter"
ORDER_URL = f"{BASE}/apiseeker/Order/CreateSellerOrder"
ORDERS_LIST_URL = f"{BASE}/apiseeker/OrdersView/SeekerGetOrdersListWithFilter"

# Minimum title word overlap (out of key words) to count as a match
MATCH_THRESHOLD = 2


class AvasamSourcer:
    def __init__(self):
        self._consumer_key = settings.avasam_consumer_key
        self._secret_key = settings.avasam_secret_key
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    @property
    def _configured(self) -> bool:
        return bool(self._consumer_key and self._secret_key)

    async def _ensure_token(self) -> bool:
        """Fetch or refresh the access token. Returns True if token is valid."""
        if not self._configured:
            return False

        now = datetime.now(timezone.utc)
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            return True

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    AUTH_URL,
                    json={"consumer_key": self._consumer_key, "secret_key": self._secret_key},
                )
            if resp.status_code == 401:
                logger.error("Avasam: invalid consumer_key or secret_key — check Settings → User Management → API Keys")
                return False
            if resp.status_code != 200:
                logger.error("Avasam auth error %s: %s", resp.status_code, resp.text[:200])
                return False

            data = resp.json()
            self._access_token = data.get("access_token")
            expires_raw = data.get("expires_at")
            if expires_raw:
                try:
                    self._token_expires_at = datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
                except Exception:
                    self._token_expires_at = None
            if not self._access_token:
                logger.error("Avasam auth: no access_token in response: %s", data)
                return False
            logger.info("Avasam: access token obtained (expires %s)", expires_raw)
            return True
        except Exception as exc:
            logger.error("Avasam auth exception: %s", exc)
            return False

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def search(self, query: str, max_results: int = 100) -> Optional[Dict]:
        """
        Find the best Avasam product matching `query`.
        Fetches inventory with optional category hint, matches by title word overlap.
        Returns None if no key set or no match found.
        """
        if not await self._ensure_token():
            return None

        # Fetch a page of inventory — no keyword search API, so we do local matching
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(
                    INVENTORY_FILTER_URL,
                    headers=self._headers,
                    json={
                        "limit": max_results,
                        "page": 1,
                        "Stock": "InStock",       # only in-stock products
                        "SortStatus": "Active",
                    },
                )
            if resp.status_code == 401:
                self._access_token = None  # force re-auth next call
                logger.warning("Avasam: token expired during search — will re-auth next call")
                return None
            if resp.status_code != 200:
                logger.warning("Avasam inventory fetch error %s", resp.status_code)
                return None

            data = resp.json()
            products = data if isinstance(data, list) else data.get("data") or data.get("products") or []
        except Exception as exc:
            logger.error("Avasam search exception: %s", exc)
            return None

        return _best_title_match(products, query)

    async def get_product(self, supplier_sku: str) -> Optional[Dict]:
        """
        Fetch current price + stock for a known SKU via inventory filter.
        Used by the monitor to recheck margin.
        """
        if not await self._ensure_token():
            return None
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    INVENTORY_FILTER_URL,
                    headers=self._headers,
                    json={"limit": 50, "page": 1, "Stock": "InStock"},
                )
            if resp.status_code != 200:
                return None
            data = resp.json()
            products = data if isinstance(data, list) else data.get("data") or []
            for p in products:
                if _get_sku(p) == supplier_sku:
                    return _parse_product(p)
        except Exception as exc:
            logger.error("Avasam get_product error: %s", exc)
        return None

    async def place_order(
        self,
        supplier_sku: str,
        quantity: int,
        recipient: Dict,
        reference: str = "",
    ) -> Optional[str]:
        """
        Submit a fulfilment order to Avasam.
        recipient keys: name, address1, address2, city, state, postcode, country_code
        Returns the Avasam order ID on success, None on failure.
        """
        if not await self._ensure_token():
            return None

        payload = {
            "Authkey": self._access_token,
            "ReferenceNumber": reference or f"eBay-{supplier_sku[:20]}",
            "ShippingServiceName": "Standard",
            "Notes": "",
            "ItemList": [{"SKU": supplier_sku, "Stock": quantity}],
            "DeliveryInfo": {
                "Name":     recipient.get("name", ""),
                "Address":  recipient.get("address1", ""),
                "City":     recipient.get("city", ""),
                "Country":  recipient.get("country_code", "GB"),
                "PostCode": recipient.get("postcode", ""),
                "PhoneNo":  "",
                "Email":    settings.owner_email,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(ORDER_URL, headers=self._headers, json=payload)
            data = resp.json()
            if resp.status_code in (200, 201) and not data.get("ErrorCode"):
                order_id = str(data.get("id") or data.get("OrderID", ""))
                logger.info("Avasam: order placed — id=%s sku=%s", order_id, supplier_sku)
                return order_id or "submitted"
            logger.error("Avasam place_order error %s: %s", resp.status_code, data)
            return None
        except Exception as exc:
            logger.error("Avasam place_order exception: %s", exc)
            return None

    async def get_order_tracking(self, order_id: str) -> Optional[Dict]:
        """Poll Avasam for dispatch/tracking info on an order."""
        if not await self._ensure_token():
            return None
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    ORDERS_LIST_URL,
                    headers=self._headers,
                    json={"limit": 50, "page": 1, "OrderStatus": "Dispatched"},
                )
            if resp.status_code != 200:
                return None
            data = resp.json()
            orders = data if isinstance(data, list) else data.get("data") or []
            for order in orders:
                oid = str(order.get("id") or order.get("Number") or "")
                if oid == order_id:
                    tracking = order.get("TrackingNumber") or order.get("tracking")
                    carrier = order.get("Carrier") or order.get("ShippingService", "")
                    if tracking:
                        return {"tracking_number": str(tracking), "carrier": str(carrier)}
        except Exception as exc:
            logger.error("Avasam get_order_tracking error: %s", exc)
        return None


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_sku(p: Dict) -> str:
    return str(p.get("SKU") or p.get("sku") or "")


def _parse_product(p: Dict) -> Optional[Dict]:
    price = float(p.get("Price") or p.get("price") or 0)
    stock = int(p.get("Stock") or p.get("stock") or 0)
    if price <= 0 or stock <= 0:
        return None

    images = p.get("Images") or p.get("images") or []
    image_url = ""
    if isinstance(images, list) and images:
        first = images[0]
        image_url = first.get("url") or first.get("URL") or str(first) if isinstance(first, dict) else str(first)

    title = str(p.get("Title") or p.get("title") or p.get("MultiTitle") or "")

    return {
        "supplier":            "avasam",
        "supplier_product_id": _get_sku(p),
        "supplier_sku":        _get_sku(p),
        "wholesale_price":     price,
        "stock_count":         stock,
        "supplier_title":      title,
        "supplier_image_url":  image_url,
    }


def _title_words(title: str) -> set:
    stop = {"for", "the", "a", "an", "with", "and", "or", "in", "on", "of", "to", "new", "uk", "set"}
    return {w for w in title.lower().split() if len(w) > 2 and w.isalpha() and w not in stop}


def _best_title_match(products: List[Dict], query: str) -> Optional[Dict]:
    """
    Return the product whose title has the most word overlap with `query`.
    Requires at least MATCH_THRESHOLD matching words.
    """
    query_words = _title_words(query)
    if not query_words:
        return None

    best_score = 0
    best_match = None

    for p in products:
        parsed = _parse_product(p)
        if parsed is None:
            continue
        product_words = _title_words(parsed["supplier_title"])
        overlap = len(query_words & product_words)
        if overlap > best_score:
            best_score = overlap
            best_match = parsed

    if best_score >= MATCH_THRESHOLD:
        logger.debug("Avasam: best match score=%d for '%s' → '%s'", best_score, query[:50], best_match["supplier_title"][:50])
        return best_match

    return None
