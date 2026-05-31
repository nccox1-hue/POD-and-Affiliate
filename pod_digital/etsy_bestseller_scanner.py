"""
Scans Etsy's API for bestselling digital download listings.
Extracts themes and keywords from top results to drive artwork generation.
"""
import logging
from typing import List, Dict
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)

ETSY_API = "https://openapi.etsy.com/v3"

# Search terms that reliably surface bestselling printable wall art
DIGITAL_SEARCH_TERMS = [
    "printable wall art",
    "printable quote poster",
    "digital download art print",
    "minimalist wall art printable",
    "inspirational quote printable",
    "botanical printable art",
    "abstract printable wall art",
    "nursery printable art",
]


def _headers() -> Dict:
    # Public listing search only needs the API key — no bearer token required
    return {
        "x-api-key": f"{settings.etsy_api_key}:{settings.etsy_api_secret}",
    }


async def find_bestselling_themes(max_results: int = 50) -> List[Dict]:
    """
    Search Etsy for bestselling digital downloads.
    Returns a list of dicts with 'title', 'tags', 'theme' extracted from top listings.
    """
    results = []
    seen_titles = set()

    async with httpx.AsyncClient(timeout=15) as client:
        for term in DIGITAL_SEARCH_TERMS[:4]:  # 4 terms per cycle to stay within rate limits
            try:
                resp = await client.get(
                    f"{ETSY_API}/application/listings/active",
                    headers=_headers(),
                    params={
                        "keywords": term,
                        "type": "download",
                        "sort_on": "score",
                        "sort_order": "desc",
                        "limit": 25,
                        "includes": ["tags"],
                    },
                )
                if resp.status_code != 200:
                    logger.warning("Etsy search error %s for '%s'", resp.status_code, term)
                    continue

                data = resp.json()
                for listing in data.get("results", []):
                    title = listing.get("title", "").strip()
                    if not title or title in seen_titles:
                        continue
                    seen_titles.add(title)
                    tags = listing.get("tags", [])
                    results.append({
                        "title": title,
                        "tags": tags,
                        "price": listing.get("price", {}).get("amount", 0) / max(listing.get("price", {}).get("divisor", 1), 1),
                        "views": listing.get("views", 0),
                        "search_term": term,
                    })

                logger.info("Digital scanner: '%s' → %d listings", term, len(data.get("results", [])))

            except Exception as e:
                logger.error("Digital scanner error for '%s': %s", term, e)

    # Sort by views descending — highest-traffic listings first
    results.sort(key=lambda x: x["views"], reverse=True)
    logger.info("Digital scanner: %d unique digital listings found", len(results))
    return results[:max_results]


def extract_theme(listing: Dict) -> str:
    """Pull the core theme/subject from a listing's title and tags."""
    title = listing["title"].lower()
    tags = [t.lower() for t in listing.get("tags", [])]

    # Common theme keywords to extract
    themes = [
        "botanical", "floral", "nature", "minimalist", "abstract",
        "inspirational", "motivational", "quote", "nursery", "animal",
        "geometric", "vintage", "watercolour", "mountain", "ocean",
        "forest", "sunset", "celestial", "moon", "garden",
    ]
    for theme in themes:
        if theme in title or any(theme in t for t in tags):
            return theme

    # Fall back to first two words of title
    words = title.split()
    return " ".join(words[:2]) if words else "minimalist art"
