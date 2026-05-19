"""
Generates SEO-optimised Etsy listing content using Claude.
Etsy SEO: title keywords in first 40 chars, 13 tags max, keyword-rich description.
"""
import asyncio
import logging
import json
from typing import Dict, Any
import anthropic
from config.settings import settings

logger = logging.getLogger(__name__)


async def generate_listing(keyword: str, theme: str, product_type: str = "t-shirt") -> Dict[str, Any]:
    """Generate a complete Etsy listing for a design keyword."""

    if not settings.anthropic_api_key:
        return _fallback_listing(keyword, product_type)

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

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
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    try:
        raw = await asyncio.get_event_loop().run_in_executor(None, _call)
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        logger.error("Listing generation error: %s", e)
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
