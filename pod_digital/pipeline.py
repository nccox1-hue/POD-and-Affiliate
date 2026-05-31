"""
Etsy Digital Downloads pipeline.

Each cycle:
  1. Scan Etsy API for bestselling digital download listings
  2. Extract themes from top results (demand signal)
  3. Generate printable wall art via Pollinations.ai
  4. Create Etsy digital listing
  5. Upload PNG files (A4, A3, 8x10, 5x7) as downloadable files
  6. Upload A4 as preview image
  7. Publish listing

Runs on APScheduler — 3x per week by default.
"""
import asyncio
import logging
import os
import tempfile

from anthropic import AsyncAnthropic

from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import DigitalListing
from pod_digital.etsy_bestseller_scanner import find_bestselling_themes, extract_theme
from pod_digital.artwork_generator import generate_artwork, PROMPT_TEMPLATES
from pod_digital.listing_publisher import (
    create_digital_listing,
    upload_digital_files,
    upload_preview_image,
    publish_listing,
)

logger = logging.getLogger(__name__)

_claude = AsyncAnthropic(api_key=settings.anthropic_api_key)

LISTINGS_PER_CYCLE = 3  # number of digital listings to create per run
PRICE_GBP = 2.49        # competitive price point for printable wall art


async def _generate_listing_copy(theme: str, reference_title: str) -> dict:
    """Use Claude Haiku to write the Etsy listing title, description, and tags."""
    prompt = f"""You are writing an Etsy listing for a printable wall art digital download.

Theme: {theme}
Reference top seller title: {reference_title}

Write:
1. TITLE (max 140 chars) — keyword-rich, specific, include "printable wall art" or "digital download"
2. DESCRIPTION (200-300 words) — what's included (4 sizes: A4, A3, 8x10, 5x7), what it suits, how to use it, instant download note
3. TAGS (13 tags, comma separated, each max 20 chars) — specific Etsy search terms

Format your response exactly as:
TITLE: <title>
DESCRIPTION: <description>
TAGS: <tag1>, <tag2>, ..."""

    msg = await _claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text.strip()

    title, description, tags_str = "", "", ""
    for line in text.split("\n"):
        if line.startswith("TITLE:"):
            title = line[6:].strip()
        elif line.startswith("DESCRIPTION:"):
            description = line[12:].strip()
        elif line.startswith("TAGS:"):
            tags_str = line[5:].strip()

    # Description may span multiple lines — grab everything after DESCRIPTION: line
    in_desc = False
    desc_lines = []
    for line in text.split("\n"):
        if line.startswith("DESCRIPTION:"):
            in_desc = True
            desc_lines.append(line[12:].strip())
        elif line.startswith("TAGS:"):
            in_desc = False
        elif in_desc:
            desc_lines.append(line)
    if desc_lines:
        description = "\n".join(desc_lines).strip()

    tags = [t.strip()[:20] for t in tags_str.split(",") if t.strip()][:13]
    return {"title": title, "description": description, "tags": tags}


class DigitalDownloadPipeline:
    async def run(self) -> int:
        """Run one cycle. Returns number of listings created."""
        if not settings.etsy_access_token or not settings.etsy_shop_id:
            logger.warning("Digital pipeline: Etsy credentials not configured — skipping")
            return 0

        logger.info("Digital download pipeline: starting cycle (target %d listings)", LISTINGS_PER_CYCLE)

        # 1. Find what's selling
        bestsellers = await find_bestselling_themes(max_results=30)
        if not bestsellers:
            logger.warning("Digital pipeline: no bestsellers found — using default themes")
            bestsellers = [{"title": t, "tags": [], "views": 0, "search_term": t}
                          for t in list(PROMPT_TEMPLATES.keys())[:LISTINGS_PER_CYCLE]]

        created = 0
        used_themes = set()

        for listing_data in bestsellers:
            if created >= LISTINGS_PER_CYCLE:
                break

            theme = extract_theme(listing_data)
            if theme in used_themes:
                continue
            used_themes.add(theme)

            logger.info("Digital pipeline: processing theme '%s'", theme)

            with tempfile.TemporaryDirectory() as tmpdir:
                # 2. Generate artwork
                file_paths = await generate_artwork(theme, tmpdir)
                if not file_paths:
                    logger.warning("Artwork generation failed for theme '%s'", theme)
                    continue

                # 3. Write listing copy
                copy = await _generate_listing_copy(theme, listing_data["title"])
                if not copy["title"]:
                    logger.warning("Listing copy generation failed for theme '%s'", theme)
                    continue

                # 4. Create listing
                listing_id = await create_digital_listing(
                    title=copy["title"],
                    description=copy["description"],
                    tags=copy["tags"],
                    price_gbp=PRICE_GBP,
                )
                if not listing_id:
                    continue

                # 5. Upload digital files (all sizes)
                uploaded = await upload_digital_files(listing_id, file_paths)
                if uploaded == 0:
                    logger.error("No files uploaded for listing %s — leaving as draft", listing_id)
                    continue

                # 6. Upload preview image (A4 = first file)
                await upload_preview_image(listing_id, file_paths[0])

                # 7. Publish
                published = await publish_listing(listing_id)
                if published:
                    created += 1
                    # Save to DB for dashboard tracking
                    async with AsyncSessionLocal() as db:
                        db.add(DigitalListing(
                            etsy_listing_id=str(listing_id),
                            title=copy["title"][:200],
                            theme=theme,
                            price_gbp=PRICE_GBP,
                            files_uploaded=uploaded,
                            status="active",
                        ))
                        await db.commit()
                    logger.info(
                        "Digital listing published: '%s' | theme=%s | files=%d",
                        copy["title"][:60], theme, uploaded,
                    )

            await asyncio.sleep(5)  # avoid hammering Etsy API

        logger.info("Digital download pipeline: %d listing(s) created this cycle", created)
        return created
