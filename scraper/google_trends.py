"""Google Trends scraper filtered to POD-relevant niches."""
import asyncio
import logging
from typing import List, Dict, Any
from pytrends.request import TrendReq
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=30))
def _fetch_related_sync(keywords: List[str]) -> List[Dict[str, Any]]:
    pytrends = TrendReq(hl="en-GB", tz=0)
    pytrends.build_payload(keywords[:5], timeframe="today 1-m", geo="GB")
    related = pytrends.related_queries()
    results = []
    for kw in keywords[:5]:
        if kw in related and related[kw].get("top") is not None:
            for _, row in related[kw]["top"].iterrows():
                results.append({
                    "keyword": row["query"],
                    "source": "google_trends",
                    "score": float(row["value"]),
                })
    return results


async def get_google_trends_for_keywords(keywords: List[str]) -> List[Dict[str, Any]]:
    try:
        results = await asyncio.get_event_loop().run_in_executor(
            None, _fetch_related_sync, keywords
        )
        logger.info("Google Trends: %d related keywords found", len(results))
        return results
    except Exception as e:
        logger.error("Google Trends error: %s", e)
        return []
