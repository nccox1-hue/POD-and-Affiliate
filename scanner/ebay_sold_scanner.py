"""
eBay Finding API scanner.
Uses findCompletedItems to fetch recently sold fixed-price listings.
Groups results by normalised title to estimate sell frequency.
Returns ScannedItem dicts ready for the source matcher.
"""
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from urllib.parse import urlencode

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

FINDING_API_PROD    = "https://svcs.ebay.com/services/search/FindingService/v1"
FINDING_API_SANDBOX = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"

# eBay UK category IDs — Avasam/BigBuy catalogue focus areas
TARGET_CATEGORIES: List[tuple] = [
    ("11700", "Home & Garden"),
    ("26395", "Garden & Patio"),
    ("1281",  "Pet Supplies"),
    ("631",   "Tools & Workshop"),
    ("220",   "Toys & Games"),
    ("14308", "Baby"),
    ("11232", "Sporting Goods"),
]


class EbaySoldScanner:
    def __init__(self):
        if settings.ebay_use_sandbox:
            self._app_id = settings.ebay_app_id_sandbox
            self._api_url = FINDING_API_SANDBOX
            logger.info("eBay scanner: using SANDBOX environment")
        else:
            self._app_id = settings.ebay_app_id
            self._api_url = FINDING_API_PROD

    def _build_params(
        self,
        category_id: str,
        min_price: float,
        max_price: float,
        days_back: int,
        page: int = 1,
    ) -> Dict[str, str]:
        from_dt = (
            datetime.now(timezone.utc) - timedelta(days=days_back)
        ).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        return {
            "OPERATION-NAME": "findCompletedItems",
            "SERVICE-VERSION": "1.13.0",
            "SECURITY-APPNAME": self._app_id,
            "RESPONSE-DATA-FORMAT": "JSON",
            "GLOBAL-ID": "EBAY-GB",
            "categoryId": category_id,
            "itemFilter(0).name": "SoldItemsOnly",
            "itemFilter(0).value": "true",
            "itemFilter(1).name": "MinPrice",
            "itemFilter(1).value": str(min_price),
            "itemFilter(1).paramName": "Currency",
            "itemFilter(1).paramValue": "GBP",
            "itemFilter(2).name": "MaxPrice",
            "itemFilter(2).value": str(max_price),
            "itemFilter(2).paramName": "Currency",
            "itemFilter(2).paramValue": "GBP",
            "itemFilter(3).name": "ListingType",
            "itemFilter(3).value": "FixedPrice",
            "itemFilter(4).name": "EndTimeFrom",
            "itemFilter(4).value": from_dt,
            "sortOrder": "BestMatch",
            "paginationInput.entriesPerPage": "100",
            "paginationInput.pageNumber": str(page),
        }

    async def scan_category(
        self,
        category_id: str,
        category_name: str,
        days_back: int = 7,
        pages: int = 1,
    ) -> List[Dict]:
        """
        Fetch sold listings for one category.
        Returns a list of raw item dicts.
        """
        if not self._app_id:
            logger.warning("eBay scanner: no EBAY_APP_ID configured")
            return []

        items = []
        for page in range(1, pages + 1):
            params = self._build_params(
                category_id,
                settings.min_ebay_price,
                settings.max_ebay_price,
                days_back,
                page,
            )
            url = f"{self._api_url}?{urlencode(params)}"
            try:
                async with httpx.AsyncClient(timeout=20) as client:
                    resp = await client.get(url)
                if resp.status_code != 200:
                    body = resp.text[:500]
                    # errorId 10001 = rate limit exceeded — stop all scanning immediately
                    if "10001" in body:
                        logger.warning(
                            "eBay scanner: daily rate limit hit — stopping scan. Resets midnight PT (~07:00 UTC). Body: %s",
                            body,
                        )
                        return items
                    logger.error(
                        "eBay scanner: HTTP %s for category %s page %d — body: %s",
                        resp.status_code, category_name, page, body,
                    )
                    break
                data = resp.json()
            except Exception as exc:
                logger.error("eBay scanner: API error for category %s page %d: %s", category_name, page, exc)
                break

            try:
                search_result = (
                    data.get("findCompletedItemsResponse", [{}])[0]
                       .get("searchResult", [{}])[0]
                )
                raw_items = search_result.get("item", [])
            except (IndexError, KeyError):
                logger.warning("eBay scanner: unexpected response shape for %s", category_name)
                break

            if not raw_items:
                break

            for raw in raw_items:
                try:
                    selling = raw.get("sellingStatus", [{}])[0]
                    state = selling.get("sellingState", [""])[0]
                    if state != "EndedWithSales":
                        continue

                    price_info = selling.get("currentPrice", [{}])[0]
                    price = float(price_info.get("__value__", 0))
                    if price <= 0:
                        continue

                    item = {
                        "ebay_item_id": raw.get("itemId", [""])[0],
                        "title": raw.get("title", [""])[0],
                        "category_id": category_id,
                        "category_name": category_name,
                        "sold_price": price,
                        "image_url": raw.get("galleryURL", [""])[0],
                    }
                    if item["title"]:
                        items.append(item)
                except Exception as e:
                    logger.debug("eBay scanner: skipping malformed item: %s", e)

            logger.info(
                "eBay scanner: %s page %d — %d sold items fetched",
                category_name, page, len(raw_items),
            )
            await asyncio.sleep(0.5)  # stay within Finding API rate limits

        return items

    async def scan_all(self, days_back: int = 7) -> List[Dict]:
        """
        Scan all TARGET_CATEGORIES and return deduplicated, frequency-ranked items.
        Items appearing in multiple listings get a higher sold_count.
        Filters to min_sold_count threshold from settings.
        """
        all_items: List[Dict] = []
        for cat_id, cat_name in TARGET_CATEGORIES:
            cat_items = await self.scan_category(cat_id, cat_name, days_back=days_back)
            all_items.extend(cat_items)
            await asyncio.sleep(1)

        logger.info("eBay scanner: %d raw sold items across %d categories", len(all_items), len(TARGET_CATEGORIES))

        # Deduplicate by normalised title — count occurrences as sell proxy
        seen: Dict[str, Dict] = {}
        for item in all_items:
            key = _normalise_title(item["title"])
            if key in seen:
                seen[key]["sold_count"] += 1
                # Keep the highest-priced sold instance as reference price
                if item["sold_price"] > seen[key]["sold_price"]:
                    seen[key]["sold_price"] = item["sold_price"]
                    seen[key]["image_url"] = item["image_url"]
            else:
                item["sold_count"] = 1
                seen[key] = item

        deduped = list(seen.values())

        # Apply min_sold_count filter
        filtered = [i for i in deduped if i["sold_count"] >= settings.min_sold_count]
        # Sort by sold_count descending (strongest signal first)
        filtered.sort(key=lambda x: x["sold_count"], reverse=True)

        logger.info(
            "eBay scanner: %d unique products, %d pass min_sold_count≥%d",
            len(deduped), len(filtered), settings.min_sold_count,
        )
        return filtered


def _normalise_title(title: str) -> str:
    """Reduce a listing title to a comparable key — lowercase, drop common filler words."""
    stop = {"for", "the", "a", "an", "with", "and", "or", "in", "on", "of", "to", "new", "uk"}
    words = [w for w in title.lower().split() if w.isalpha() and w not in stop]
    return " ".join(sorted(words[:8]))  # sort so word-order variations match
