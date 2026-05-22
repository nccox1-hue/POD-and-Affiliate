"""
Scrapes trending keywords for POD design research.
Etsy's own endpoints are Cloudflare-blocked, so autocomplete uses Google's
suggest API instead — same buyer-intent signal, no auth needed.
"""
import asyncio
import logging
import httpx
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

GOOGLE_SUGGEST_URL = "https://suggestqueries.google.com/complete/search"


async def get_etsy_autocomplete(query: str) -> List[str]:
    """Get buyer-intent search suggestions for a keyword via Google autocomplete."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                GOOGLE_SUGGEST_URL,
                params={"client": "firefox", "q": f"{query} t-shirt", "hl": "en"},
            )
            if resp.status_code != 200:
                logger.debug("Google suggest returned %d for '%s'", resp.status_code, query)
                return []
            data = resp.json()
            return [s for s in data[1] if isinstance(s, str)]
    except Exception as e:
        logger.debug("Autocomplete failed for '%s': %s", query, e)
        return []


async def get_etsy_trending_for_theme(theme_keywords: List[str]) -> List[Dict[str, Any]]:
    """Build a list of trending keywords by expanding theme seed keywords via autocomplete."""
    all_suggestions = []
    for seed in theme_keywords[:4]:
        suggestions = await get_etsy_autocomplete(seed)
        for s in suggestions:
            all_suggestions.append({
                "keyword": s,
                "source": "google_autocomplete",
                "score": 70.0,
            })
        await asyncio.sleep(0.3)
    return all_suggestions


async def scrape_etsy_bestsellers(category: str = "t-shirts") -> List[Dict[str, Any]]:
    """Get bestseller-style keywords via Google autocomplete on the category."""
    suggestions = await get_etsy_autocomplete(f"best {category}")
    results = []
    for s in suggestions:
        if len(s) > 5:
            results.append({
                "keyword": s,
                "source": "google_autocomplete_bestseller",
                "score": 80.0,
            })
    return results
