"""
Generates SEO-optimised Etsy listing content using Gemini Flash.
Etsy SEO: title keywords in first 40 chars, 13 tags max, keyword-rich description.
"""
import asyncio
import logging
import json
from typing import Dict, Any
from google import genai
from config.settings import settings

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


async def generate_listing(keyword: str, theme: str, product_type: str = "t-shirt") -> Dict[str, Any]:
    """Generate a complete Etsy listing for a design keyword."""

    if not settings.gemini_api_key:
        return _fallback_listing(keyword, product_type)

    prompt = f"""Create an SEO-optimised Etsy listing for a print-on-demand {product_type}.

Design keyword: {keyword}
Theme: {theme}
Product: {product_type}

Output ONLY valid JSON:
{{
  "title": "Etsy title max 140 chars, keyword-rich, most important keyword first",
  "description": "Full Etsy description 150-200 words. Include: what it is, who it's for, sizing note, gift idea mention. Natural keyword use.",
  "tags": ["exactly", "13", "tags", "each", "max", "20", "chars", "no", "plurals", "mix", "broad", "and", "specific"],
  "price_note": "suggested price range in GBP e.g. 18-22",
  "materials": ["Cotton", "Polyester"],
  "occasion": ["Birthday", "Christmas", "Gift"]
}}"""

    def _call():
        client = _get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()

    for attempt in range(2):
        try:
            raw = await asyncio.get_event_loop().run_in_executor(None, _call)
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            if "429" in str(e) and attempt == 0:
                logger.warning("Gemini rate limited — retrying in 45s")
                await asyncio.sleep(45)
                continue
            logger.error("Listing generation error: %s", e)
            return _fallback_listing(keyword, product_type)
    return _fallback_listing(keyword, product_type)


def _fallback_listing(keyword: str, product_type: str) -> Dict[str, Any]:
    return {
        "title": f"{keyword.title()} {product_type.title()} | Funny Gift | Unisex Tee",
        "description": (
            f"Looking for the perfect gift? This {keyword} {product_type} is ideal for anyone "
            f"who loves {keyword}. Printed on premium quality fabric, soft and comfortable. "
            f"Makes a brilliant birthday, Christmas or just-because gift. Available in a full "
            f"range of sizes. Check our size guide before ordering."
        ),
        "tags": [keyword[:20], product_type, "funny gift", "novelty gift",
                 "gift for him", "gift for her", "birthday gift",
                 "unisex tee", "graphic tee", "cool shirt",
                 "trending", "sarcastic", "humour"],
        "price_note": "18-22",
        "materials": ["Cotton", "Polyester"],
        "occasion": ["Birthday", "Christmas", "Gift"],
    }
