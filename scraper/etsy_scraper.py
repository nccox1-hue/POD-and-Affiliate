"""
Scrapes Etsy for trending searches and bestselling design keywords.
Uses Etsy's public autocomplete endpoint — no API key needed.
"""
import asyncio
import logging
import httpx
from typing import List, Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

ETSY_AUTOCOMPLETE = "https://www.etsy.com/api/v3/ajax/bespoke/member/neu/specs/async/search-bar-page-component"
ETSY_TRENDING_URL = "https://www.etsy.com/api/v3/ajax/bespoke/member/neu/specs/async/search-trending"


async def get_etsy_autocomplete(query: str) -> List[str]:
    """Get Etsy search suggestions for a keyword — shows what buyers are searching."""
    headers = {"x-detected-locale": "GBP|en-GB|GB", "User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
            resp = await client.get(
                "https://completion.etsy.com/ajax/completion",
                params={"query": query, "limit": 10, "source": "topnav"},
            )
            data = resp.json()
            results = []
            for item in data.get("results", []):
                if isinstance(item, dict):
                    results.append(item.get("query", ""))
                elif isinstance(item, str):
                    results.append(item)
            return [r for r in results if r]
    except Exception as e:
        logger.debug("Etsy autocomplete failed for '%s': %s", query, e)
        return []


async def get_etsy_trending_for_theme(theme_keywords: List[str]) -> List[Dict[str, Any]]:
    """Build a list of trending Etsy keywords by expanding theme seed keywords."""
    all_suggestions = []
    for seed in theme_keywords[:4]:
        suggestions = await get_etsy_autocomplete(seed)
        for s in suggestions:
            all_suggestions.append({
                "keyword": s,
                "source": "etsy_autocomplete",
                "score": 70.0,
            })
        await asyncio.sleep(0.5)
    return all_suggestions


async def scrape_etsy_bestsellers(category: str = "t-shirts") -> List[Dict[str, Any]]:
    """Scrape Etsy bestseller titles for design inspiration."""
    from bs4 import BeautifulSoup

    url = f"https://www.etsy.com/search?q={category}&sort_on=score&view_type=gallery"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-GB,en;q=0.9",
    }
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=headers, follow_redirects=True) as client:
            resp = await client.get(url)
            soup = BeautifulSoup(resp.text, "lxml")

            # Extract listing titles
            for title_el in soup.select("h3.v2-listing-card__title")[:20]:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    results.append({
                        "keyword": title,
                        "source": "etsy_bestseller",
                        "score": 80.0,
                    })
    except Exception as e:
        logger.debug("Etsy bestseller scrape failed: %s", e)

    return results
