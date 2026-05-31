"""
Etsy Professional Templates pipeline — Stream A (second product).

Each cycle:
  1. Picks next template from the catalogue
  2. Generates the Excel file using openpyxl
  3. Creates a preview image (screenshot-style PNG) via Pollinations.ai
  4. Creates Etsy digital listing at £10-£30
  5. Uploads the .xlsx file as the digital download
  6. Uploads preview image
  7. Publishes listing

Runs every 48h — slower cadence than wall art since these are higher-value products.
Price point: £10-£30 vs £2.49 for wall art. Target: 50 sales/month = £700-£1,000/month.
"""
import asyncio
import logging
import os
import tempfile

import httpx
from PIL import Image

from anthropic import AsyncAnthropic
from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import DigitalListing
from pod_digital.template_generator import TEMPLATES, generate_template
from pod_digital.listing_publisher import (
    create_digital_listing,
    upload_digital_files,
    upload_preview_image,
    publish_listing,
)

logger = logging.getLogger(__name__)
_claude = AsyncAnthropic(api_key=settings.anthropic_api_key)

# Taxonomy ID for Templates (Etsy: Patterns & How To category is closest)
TEMPLATE_TAXONOMY_ID = 2078
LISTINGS_PER_CYCLE = 1  # one template per run — quality over quantity


async def _generate_preview_image(template: dict, output_dir: str) -> str:
    """Generate a professional-looking preview image for the template listing."""
    prompt = (
        f"Professional Excel spreadsheet screenshot preview, {template['theme']} theme, "
        f"showing a clean {template['id'].replace('_', ' ')} with blue header rows, "
        f"data tables, charts, white background, modern business style, "
        f"high quality product mockup for digital download listing"
    ).replace(" ", "%20")

    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1200&height=900&model=flux&nologo=true"
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url)
        if resp.status_code == 200:
            path = os.path.join(output_dir, "preview.png")
            with open(path, "wb") as f:
                f.write(resp.content)
            return path
    except Exception as e:
        logger.warning("Preview image generation failed: %s", e)
    return ""


async def _write_listing_copy(template: dict) -> dict:
    """Generate enhanced listing copy for a professional template."""
    msg = await _claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": f"""Write Etsy listing copy for a professional Excel template.

Template: {template['title']}
Description to enhance: {template['description']}
Tags already set: {', '.join(template['tags'][:5])}

Write:
TITLE: (max 140 chars, keep keywords)
DESCRIPTION: (enhance the existing description, 150-200 words, professional tone, mention instant download)

Format exactly as TITLE: and DESCRIPTION:"""}]
    )
    text = msg.content[0].text
    title, desc = template["title"], template["description"]
    for line in text.split("\n"):
        if line.startswith("TITLE:"):
            title = line[6:].strip()[:140]
        elif line.startswith("DESCRIPTION:"):
            desc = line[12:].strip()
    return {"title": title, "description": desc}


class TemplatePipeline:
    def __init__(self):
        self._current_index = 0

    async def run(self) -> int:
        if not settings.etsy_access_token or not settings.etsy_shop_id:
            logger.warning("Template pipeline: Etsy credentials not configured")
            return 0

        # Check which templates haven't been listed yet
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            result = await db.execute(
                select(DigitalListing.theme)
                .where(DigitalListing.theme.like("tmpl_%"))
            )
            listed_themes = {r[0] for r in result.all()}

        pending = [t for t in TEMPLATES if f"tmpl_{t['id']}" not in listed_themes]
        if not pending:
            logger.info("Template pipeline: all templates listed — cycle complete")
            return 0

        created = 0
        for template in pending[:LISTINGS_PER_CYCLE]:
            logger.info("Template pipeline: creating listing for '%s'", template["id"])

            with tempfile.TemporaryDirectory() as tmpdir:
                # Generate the Excel file
                excel_files = generate_template(template["id"], tmpdir)
                if not excel_files:
                    logger.error("Template generation failed for %s", template["id"])
                    continue

                # Generate preview image
                preview_path = await _generate_preview_image(template, tmpdir)

                # Write listing copy
                copy = await _write_listing_copy(template)

                # Create listing
                listing_id = await create_digital_listing(
                    title=copy["title"],
                    description=copy["description"],
                    tags=template["tags"],
                    price_gbp=template["price"],
                )
                if not listing_id:
                    continue

                # Upload Excel file
                uploaded = await upload_digital_files(listing_id, excel_files)
                if uploaded == 0:
                    logger.error("No files uploaded for template %s", template["id"])
                    continue

                # Upload preview
                if preview_path and os.path.exists(preview_path):
                    await upload_preview_image(listing_id, preview_path)

                # Publish
                if await publish_listing(listing_id):
                    async with AsyncSessionLocal() as db:
                        db.add(DigitalListing(
                            etsy_listing_id=str(listing_id),
                            title=copy["title"][:200],
                            theme=f"tmpl_{template['id']}",
                            price_gbp=template["price"],
                            files_uploaded=uploaded,
                            status="active",
                        ))
                        await db.commit()
                    created += 1
                    logger.info(
                        "Template listing published: '%s' @ £%.2f",
                        template["id"], template["price"],
                    )

            await asyncio.sleep(5)

        logger.info("Template pipeline: %d listing(s) created", created)
        return created
