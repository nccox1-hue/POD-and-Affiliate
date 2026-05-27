"""
Generates eBay listing content — title and description — for arbitrage listings.
Input: supplier product title + eBay sold listing title (both used for context).
Priority: Claude (Anthropic) → Gemini Flash → hardcoded fallback.
"""
import asyncio
import logging
import json
from typing import Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """You're writing an eBay listing for a UK dropship seller.
Write like a real seller — direct, factual, a bit of personality. British spelling throughout.

eBay sold title (what buyers are already buying): {ebay_title}
Supplier product title (what we're stocking): {supplier_title}

Rules — follow exactly:
- Title: 80 characters max (eBay hard limit). Lead with the strongest search keyword.
  No ALL CAPS. No misleading terms. Match what buyers search for.
- Description: 150-250 words. Talk directly to the buyer ("you/your").
  Short punchy sentences. What is it, what does it do, key specs if relevant.
  Mention: dispatched within 2-3 business days, UK seller.
  Do NOT use: "perfect for", "unique", "high quality", "look no further",
  "elevate your", "whether you", "this is the", "amazing"
- No Etsy language, no print-on-demand language, no personalisation offers.

Output ONLY valid JSON, no markdown fences:
{{
  "title": "...",
  "description": "..."
}}"""


def _parse_json(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


async def _generate_claude(ebay_title: str, supplier_title: str) -> Dict[str, Any]:
    import anthropic
    prompt = _PROMPT_TEMPLATE.format(ebay_title=ebay_title, supplier_title=supplier_title)

    def _call():
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    raw = await asyncio.get_event_loop().run_in_executor(None, _call)
    return _parse_json(raw)


async def _generate_gemini(ebay_title: str, supplier_title: str) -> Dict[str, Any]:
    from google import genai
    prompt = _PROMPT_TEMPLATE.format(ebay_title=ebay_title, supplier_title=supplier_title)

    def _call():
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()

    for attempt in range(2):
        try:
            raw = await asyncio.get_event_loop().run_in_executor(None, _call)
            return _parse_json(raw)
        except Exception as e:
            if "429" in str(e) and attempt == 0:
                logger.warning("Gemini rate limited — retrying in 45s")
                await asyncio.sleep(45)
                continue
            raise


async def generate_listing(ebay_title: str, supplier_title: str) -> Dict[str, Any]:
    """Generate eBay title + description. Tries Claude, then Gemini, then fallback."""
    if settings.anthropic_api_key:
        try:
            result = await _generate_claude(ebay_title, supplier_title)
            logger.info("Listing generated (Claude) for '%s'", ebay_title[:50])
            return result
        except Exception as e:
            logger.warning("Claude listing failed, trying Gemini: %s", e)

    if settings.gemini_api_key:
        try:
            result = await _generate_gemini(ebay_title, supplier_title)
            logger.info("Listing generated (Gemini) for '%s'", ebay_title[:50])
            return result
        except Exception as e:
            logger.warning("Gemini listing failed, using fallback: %s", e)

    logger.warning("Using fallback listing copy for '%s'", ebay_title[:50])
    return _fallback_listing(ebay_title, supplier_title)


def _fallback_listing(ebay_title: str, supplier_title: str) -> Dict[str, Any]:
    title = (ebay_title or supplier_title)[:80]
    name = title.rstrip(",.!").strip()
    return {
        "title": title,
        "description": (
            f"{name} — in stock and ready to go.\n\n"
            f"Good quality item at a fair price. Exactly what it says on the tin.\n\n"
            f"Dispatched within 2-3 business days from our UK supplier. "
            f"Tracked shipping included. Any questions — just ask."
        ),
    }
