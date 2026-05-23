"""
Standalone listing generator — no Printful or Etsy API required.
Generates design images + listing copy for manual Etsy upload.

Output: data/designs/<keyword>.png  +  data/listings_output.txt
"""
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime

from generator.design_generator import generate_design, build_design_prompt
from generator.listing_generator import generate_listing

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

KEYWORDS = [
    ("cat mum", "cute"),
    ("dog dad", "funny"),
    ("hiking mountains", "adventure"),
]

OUTPUT_FILE = Path("data/listings_output.txt")


async def generate_one(keyword: str, theme: str) -> dict:
    safe = "".join(c for c in keyword if c.isalnum() or c == " ").replace(" ", "_")
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{safe}_{timestamp}"

    logger.info("--- Starting: '%s' ---", keyword)

    design_prompt = await build_design_prompt(keyword, theme)
    logger.info("Prompt: %s", design_prompt)

    image_path = await generate_design(design_prompt, filename)
    if not image_path:
        logger.error("Image generation failed for '%s'", keyword)
        return {}

    # Rate limit gap between Gemini calls
    await asyncio.sleep(15)

    listing = await generate_listing(keyword, theme, "t-shirt")

    return {
        "keyword": keyword,
        "image_path": image_path,
        "design_prompt": design_prompt,
        "listing": listing,
    }


def write_output(results: list):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("=" * 60)
    lines.append(f"LISTINGS GENERATED — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)

    for r in results:
        if not r:
            continue
        listing = r["listing"]
        lines.append("")
        lines.append(f"KEYWORD: {r['keyword']}")
        lines.append(f"IMAGE:   {r['image_path']}")
        lines.append("-" * 60)
        lines.append(f"TITLE:\n{listing.get('title', '')}")
        lines.append("")
        lines.append(f"DESCRIPTION:\n{listing.get('description', '')}")
        lines.append("")
        tags = listing.get("tags", [])
        lines.append(f"TAGS ({len(tags)}):\n{', '.join(tags)}")
        lines.append("")
        lines.append(f"PRICE SUGGESTION: {listing.get('price_note', '18-22')} GBP")
        lines.append("=" * 60)

    text = "\n".join(lines)
    OUTPUT_FILE.write_text(text, encoding="utf-8")
    print(text)
    logger.info("Saved to %s", OUTPUT_FILE)


async def main():
    results = []
    for keyword, theme in KEYWORDS:
        result = await generate_one(keyword, theme)
        results.append(result)
        # Gap between listings to avoid Gemini rate limits
        await asyncio.sleep(10)

    write_output(results)


if __name__ == "__main__":
    asyncio.run(main())
