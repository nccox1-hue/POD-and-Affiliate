"""
Etsy keyword scraper — uses Etsy API v3 public listing search.
Searches active listings by seed keyword and extracts their tags as keyword signals.
Tags are genuine buyer-intent terms that sellers have researched for Etsy SEO.
Falls back to Google autocomplete if no API key is configured.
"""
import asyncio
import logging
import httpx
from typing import List, Dict, Any
from collections import Counter

from config.settings import settings

logger = logging.getLogger(__name__)

ETSY_API = "https://openapi.etsy.com/v3/application"
GOOGLE_SUGGEST_URL = "https://suggestqueries.google.com/complete/search"


async def _search_etsy_listings(keyword: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Search Etsy active listings by keyword. Returns raw listing dicts."""
    if not settings.etsy_api_key:
        return []
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(
                f"{ETSY_API}/listings/active",
                headers={"x-api-key": settings.etsy_api_key},
                params={
                    "keywords": keyword,
                    "limit": limit,
                    "sort_on": "score",
                    "sort_order": "desc",
                },
            )
            if resp.status_code == 200:
                return resp.json().get("results", [])
            logger.debug("Etsy API returned %d for '%s'", resp.status_code, keyword)
            return []
    except Exception as e:
        logger.debug("Etsy API search failed for '%s': %s", keyword, e)
        return []


async def get_etsy_trending_for_theme(theme_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Search Etsy listings for each seed keyword and extract their tags.
    Tags are genuine Etsy SEO keywords — stronger signal than Google autocomplete.
    """
    if not settings.etsy_api_key:
        return await _google_autocomplete_fallback(theme_keywords)

    tag_counts: Counter = Counter()

    for seed in theme_keywords[:4]:
        listings = await _search_etsy_listings(f"{seed} t-shirt", limit=25)
        for listing in listings:
            for tag in listing.get("tags", []):
                tag = tag.strip().lower()
                if len(tag) > 4 and tag not in ("shirt", "tshirt", "t-shirt", "tee"):
                    tag_counts[tag] += 1
        await asyncio.sleep(0.5)

    results = []
    for tag, count in tag_counts.most_common(40):
        score = min(95.0, 60.0 + count * 5.0)
        results.append({"keyword": tag, "source": "etsy_api_tags", "score": score})

    logger.info("Etsy API scraper: %d tag keywords from %d seeds", len(results), len(theme_keywords[:4]))
    return results


async def scrape_etsy_bestsellers(category: str = "t-shirts") -> List[Dict[str, Any]]:
    """
    Get bestseller-style keywords by searching Etsy by category sorted by score.
    Extracts tags from top listings as high-intent keyword signals.
    """
    if not settings.etsy_api_key:
        return await _google_bestseller_fallback(category)

    listings = await _search_etsy_listings(category, limit=25)
    tag_counts: Counter = Counter()
    for listing in listings:
        for tag in listing.get("tags", []):
            tag = tag.strip().lower()
            if len(tag) > 4 and tag not in ("shirt", "tshirt", "t-shirt", "tee"):
                tag_counts[tag] += 1

    results = []
    for tag, count in tag_counts.most_common(20):
        score = min(95.0, 65.0 + count * 5.0)
        results.append({"keyword": tag, "source": "etsy_api_bestseller", "score": score})

    logger.info("Etsy API bestseller: %d keywords for '%s'", len(results), category)
    return results


async def _google_autocomplete_fallback(theme_keywords: List[str]) -> List[Dict[str, Any]]:
    """Google autocomplete fallback if Etsy API key is unavailable."""
    all_suggestions = []
    for seed in theme_keywords[:4]:
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(
                    GOOGLE_SUGGEST_URL,
                    params={"client": "firefox", "q": f"{seed} t-shirt", "hl": "en"},
                )
                if resp.status_code == 200:
                    for s in resp.json()[1]:
                        if isinstance(s, str):
                            all_suggestions.append({"keyword": s, "source": "google_autocomplete", "score": 60.0})
        except Exception as e:
            logger.debug("Google autocomplete fallback failed: %s", e)
        await asyncio.sleep(0.3)
    return all_suggestions


async def _google_bestseller_fallback(category: str) -> List[Dict[str, Any]]:
    """Google autocomplete bestseller fallback."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                GOOGLE_SUGGEST_URL,
                params={"client": "firefox", "q": f"best {category}", "hl": "en"},
            )
            if resp.status_code == 200:
                return [
                    {"keyword": s, "source": "google_autocomplete_bestseller", "score": 70.0}
                    for s in resp.json()[1]
                    if isinstance(s, str) and len(s) > 5
                ]
    except Exception as e:
        logger.debug("Google bestseller fallback failed: %s", e)
    return []
