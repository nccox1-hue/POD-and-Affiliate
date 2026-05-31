"""
eBay sold listings scanner — Playwright-based replacement for the decommissioned Finding API.
Uses keyword searches on eBay UK sold/completed listings.
Returns the same ScannedItem dict format as the original API-based scanner.
"""
import asyncio
import logging
import re
from typing import Dict, List

from playwright.async_api import async_playwright, BrowserContext

from config.settings import settings

logger = logging.getLogger(__name__)

# Keyword search terms mapped to category metadata.
# Multiple terms per category increases coverage; deduplication handles overlaps.
SEARCH_TARGETS: List[Dict] = [
    {"keywords": ["home storage organisation", "kitchen gadgets", "bathroom accessories"],
     "category_id": "11700", "category_name": "Home & Garden"},
    {"keywords": ["garden tools outdoor", "plant pots garden decor"],
     "category_id": "26395", "category_name": "Garden & Patio"},
    {"keywords": ["dog accessories pet", "cat supplies pet toys"],
     "category_id": "1281",  "category_name": "Pet Supplies"},
    {"keywords": ["hand tools diy", "power tool accessories"],
     "category_id": "631",   "category_name": "Tools & Workshop"},
    {"keywords": ["children toys games", "kids outdoor toys"],
     "category_id": "220",   "category_name": "Toys & Games"},
    {"keywords": ["baby clothes accessories", "nursery baby gear"],
     "category_id": "14308", "category_name": "Baby"},
    {"keywords": ["fitness equipment gym", "sports outdoor activity"],
     "category_id": "11232", "category_name": "Sporting Goods"},
]

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _parse_price(text: str) -> float:
    """Extract the first numeric value from strings like '£12.99' or '£8.00 to £20.00'."""
    matches = re.findall(r"\d+\.?\d*", text.replace(",", ""))
    return float(matches[0]) if matches else 0.0


def _normalise_title(title: str) -> str:
    """Reduce title to a dedup key — lowercase, drop filler words, sort remainder."""
    stop = {"for", "the", "a", "an", "with", "and", "or", "in", "on", "of", "to", "new", "uk"}
    words = [w for w in title.lower().split() if w.isalpha() and w not in stop]
    return " ".join(sorted(words[:8]))


def _search_url(keyword: str) -> str:
    kw = keyword.replace(" ", "+")
    return (
        f"https://www.ebay.co.uk/sch/i.html?_nkw={kw}"
        f"&LH_Complete=1&LH_Sold=1"
        f"&LH_BIN=1"
        f"&LH_PrefLoc=1"
        f"&_udlo={int(settings.min_ebay_price)}"
        f"&_udhi={int(settings.max_ebay_price)}"
        f"&_ipg=240"
        f"&_sop=13"
    )


async def _scrape_keyword(page, keyword: str, category_id: str, category_name: str) -> List[Dict]:
    """Scrape one keyword search and return item dicts."""
    items = []
    url = _search_url(keyword)
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        await asyncio.sleep(2.5)

        cards = await page.query_selector_all("li.s-card")
        for card in cards:
            try:
                title_el = await card.query_selector(".s-card__title")
                if not title_el:
                    continue
                title = (await title_el.inner_text()).strip()
                if not title or "shop on ebay" in title.lower():
                    continue

                price_el = await card.query_selector(".s-card__price")
                price = _parse_price(await price_el.inner_text() if price_el else "")
                if price < settings.min_ebay_price or price > settings.max_ebay_price:
                    continue

                item_id = await card.get_attribute("data-listingid") or ""

                img_el = await card.query_selector("img")
                image_url = ""
                if img_el:
                    image_url = (
                        await img_el.get_attribute("src") or
                        await img_el.get_attribute("data-src") or ""
                    )
                    # Skip eBay placeholder/logo images
                    if "ebaystatic" in image_url:
                        image_url = ""

                items.append({
                    "ebay_item_id": item_id,
                    "title": title,
                    "category_id": category_id,
                    "category_name": category_name,
                    "sold_price": price,
                    "image_url": image_url,
                })

            except Exception as e:
                logger.debug("Scanner: skipping card: %s", e)

        logger.info(
            "eBay scanner: '%s' — %d sold items fetched", keyword, len(items)
        )
    except Exception as e:
        logger.error("eBay scanner: error on '%s': %s", keyword, e)

    return items


class EbaySoldScanner:
    """
    Drop-in replacement for the original Finding API scanner.
    Public interface (scan_category / scan_all) and return format are identical.
    """

    async def scan_category(
        self,
        category_id: str,
        category_name: str,
        days_back: int = 7,
        pages: int = 1,
        _page=None,
    ) -> List[Dict]:
        """Scan one category's keywords. _page is an optional shared Playwright page."""
        target = next(
            (t for t in SEARCH_TARGETS if t["category_id"] == category_id),
            {"keywords": [category_name.lower()], "category_id": category_id, "category_name": category_name}
        )
        items = []
        for kw in target["keywords"]:
            kw_items = await _scrape_keyword(_page, kw, category_id, category_name)
            items.extend(kw_items)
            await asyncio.sleep(2.0)
        return items

    async def scan_all(self, days_back: int = 7) -> List[Dict]:
        """
        Scan all SEARCH_TARGETS. Returns deduplicated, frequency-ranked items.
        Identical return format to the original Finding API scanner.
        """
        all_items: List[Dict] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(
                user_agent=_USER_AGENT,
                viewport={"width": 1280, "height": 900},
                locale="en-GB",
                timezone_id="Europe/London",
            )
            # Block fonts and media — speeds up loading without losing item data
            await ctx.route(
                "**/*.{woff,woff2,ttf,otf,mp4,webm}",
                lambda route: route.abort()
            )
            page = await ctx.new_page()

            # Prime cookies via homepage — prevents error pages on first search
            await page.goto("https://www.ebay.co.uk", wait_until="domcontentloaded", timeout=30_000)
            await asyncio.sleep(1.5)

            for target in SEARCH_TARGETS:
                for kw in target["keywords"]:
                    kw_items = await _scrape_keyword(
                        page, kw, target["category_id"], target["category_name"]
                    )
                    all_items.extend(kw_items)
                    await asyncio.sleep(3.0)  # polite gap between searches

            await browser.close()

        logger.info(
            "eBay scanner: %d raw sold items across %d search terms",
            len(all_items), sum(len(t["keywords"]) for t in SEARCH_TARGETS),
        )

        # Deduplicate by normalised title — identical logic to original scanner
        seen: Dict[str, Dict] = {}
        for item in all_items:
            key = _normalise_title(item["title"])
            if key in seen:
                seen[key]["sold_count"] += 1
                if item["sold_price"] > seen[key]["sold_price"]:
                    seen[key]["sold_price"] = item["sold_price"]
                    seen[key]["image_url"] = item["image_url"]
            else:
                item["sold_count"] = 1
                seen[key] = item

        deduped = list(seen.values())
        filtered = [i for i in deduped if i["sold_count"] >= settings.min_sold_count]
        filtered.sort(key=lambda x: x["sold_count"], reverse=True)

        logger.info(
            "eBay scanner: %d unique products, %d pass min_sold_count≥%d",
            len(deduped), len(filtered), settings.min_sold_count,
        )
        return filtered
