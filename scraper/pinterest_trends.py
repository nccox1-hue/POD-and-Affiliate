"""
Trend discovery scraper using Google autocomplete with gift/aesthetic context queries.
Pinterest's public trends API endpoint no longer exists (returns 404).
Google autocomplete with discovery-style queries provides equivalent signal.
"""
import asyncio
import logging
import httpx
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

GOOGLE_SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

# Context suffixes that surface discovery/gift-style queries — mimics Pinterest intent
_DISCOVERY_CONTEXTS = ["gift idea", "aesthetic gift", "trendy design"]


async def get_pinterest_trends(country: str = "GB") -> List[Dict[str, Any]]:
    """Fetch discovery-style trending keywords via Google autocomplete."""
    seed_terms = ["funny", "cute", "vintage", "nature", "motivational", "animal"]
    results: List[Dict[str, Any]] = []
    seen: set = set()

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for seed in seed_terms:
            for context in _DISCOVERY_CONTEXTS[:2]:
                try:
                    resp = await client.get(
                        GOOGLE_SUGGEST_URL,
                        params={"client": "firefox", "q": f"{seed} {context}", "hl": "en"},
                    )
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    for i, suggestion in enumerate(data[1]):
                        if not isinstance(suggestion, str):
                            continue
                        key = suggestion.lower().strip()
                        if key not in seen:
                            seen.add(key)
                            results.append({
                                "keyword": suggestion,
                                "source": "google_autocomplete_discovery",
                                "score": max(0.0, 90.0 - (len(results) * 1.5)),
                            })
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logger.debug("Discovery autocomplete failed for '%s %s': %s", seed, context, e)

    logger.info("Discovery trends: %d keywords found", len(results))
    return results
