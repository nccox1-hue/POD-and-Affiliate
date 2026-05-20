"""
Pinterest Trends scraper.
Uses Pinterest's public trends endpoint — no API key needed.
Pinterest is highly visual and design-driven, making it ideal for POD trend research.
"""
import logging
import httpx
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

PINTEREST_TRENDS_URL = "https://trends.pinterest.com/api/v1/trending_searches"


async def get_pinterest_trends(country: str = "GB") -> List[Dict[str, Any]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://trends.pinterest.com/",
    }
    # GB not always supported — fall back to US
    countries = [country, "US"] if country != "US" else ["US"]
    for country_code in countries:
        try:
            async with httpx.AsyncClient(timeout=15, headers=headers, follow_redirects=True) as client:
                resp = await client.get(
                    PINTEREST_TRENDS_URL,
                    params={"country_code": country_code, "limit": 50},
                )
                if resp.status_code != 200:
                    logger.debug("Pinterest trends %s returned %d", country_code, resp.status_code)
                    continue
                data = resp.json()
            results = []
            for i, item in enumerate(data.get("trending_searches", [])):
                trend_name = item.get("normalized_term") or item.get("term", "")
                if trend_name:
                    results.append({
                        "keyword": trend_name,
                        "source": "pinterest_trends",
                        "score": max(0.0, 100.0 - (i * 2)),
                    })
            logger.info("Pinterest Trends (%s): %d trends found", country_code, len(results))
            return results
        except Exception as e:
            logger.debug("Pinterest trends failed for %s: %s", country_code, e)
    return []
