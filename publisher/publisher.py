"""
Orchestrates the full pipeline for one design opportunity:
trend keyword → design prompt → image → listing copy → Printful product → Etsy listing
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import settings
from config.themes import THEME_CATALOGUE
from generator.design_generator import generate_design, build_design_prompt
from generator.listing_generator import generate_listing
from publisher.printful_client import PrintfulClient, PRODUCT_VARIANTS
from publisher.etsy_client import EtsyClient
from database.db import AsyncSessionLocal
from database.models import DesignJob

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self):
        self.printful = PrintfulClient()
        self.etsy = EtsyClient()

    async def run(self, opportunity: Dict[str, Any]) -> bool:
        """
        Full pipeline for one design opportunity.
        Returns True on success.
        """
        keyword = opportunity["keyword"]
        theme = opportunity.get("theme", "funny")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_kw = "".join(c for c in keyword[:30] if c.isalnum() or c in " _").replace(" ", "_")
        filename = f"{safe_kw}_{timestamp}"

        logger.info("Publisher: starting pipeline for '%s' (theme: %s)", keyword, theme)

        # 1. Generate AI image prompt
        design_prompt = await build_design_prompt(keyword, theme)
        logger.info("Design prompt: %s", design_prompt)

        # 2. Generate design image
        image_path = await generate_design(design_prompt, filename)
        if not image_path:
            logger.error("Design generation failed for '%s'", keyword)
            return False

        # 3. Upload design to Printful
        design_url = await self.printful.upload_design_file(image_path, f"{filename}.png")

        # 4. Generate listing copy (title, description, tags)
        # Brief pause to avoid Gemini free-tier rate limit (design prompt + listing = 2 calls/listing)
        await asyncio.sleep(15)
        product_id = settings.product_id_list[0] if settings.product_id_list else 71
        product_name = PRODUCT_VARIANTS.get(product_id, {}).get("name", "T-Shirt")
        listing = await generate_listing(keyword, theme, product_name)

        # 5. Calculate price
        # Printful base cost for Bella+Canvas 3001 is ~£9-11
        # We default to £10 base and apply the multiplier
        base_cost = 10.0
        retail_price = round(base_cost * settings.price_multiplier, 2)

        # 6. Create Printful sync product (handles fulfilment)
        printful_product = None
        if design_url and settings.printful_api_key:
            printful_product = await self.printful.create_sync_product(
                name=listing["title"][:140],
                description=listing["description"],
                design_url=design_url,
                product_id=product_id,
                retail_price=str(retail_price),
            )

        # 7. Get mockup image (for Etsy listing photos)
        mockup_url = None
        if design_url and settings.printful_api_key:
            variants = PRODUCT_VARIANTS.get(product_id, {}).get("variants", [])
            mockup_url = await self.printful.get_mockup_url(product_id, variants[:1], design_url)

        # 8. Create Etsy draft listing
        etsy_listing = None
        if settings.etsy_access_token:
            etsy_listing = await self.etsy.create_draft_listing(
                title=listing["title"],
                description=listing["description"],
                price_gbp=retail_price,
                tags=listing["tags"],
                materials=listing.get("materials", ["Cotton"]),
            )

            if etsy_listing:
                listing_id = etsy_listing["listing_id"]

                # Upload design image to listing
                await self.etsy.upload_listing_image(listing_id, image_path, rank=1)

                # Auto-publish (set state=draft above to review first — change to active to auto-publish)
                # await self.etsy.publish_listing(listing_id)

        # 9. Save to database
        async with AsyncSessionLocal() as db:
            job = DesignJob(
                keyword=keyword,
                theme=theme,
                design_prompt=design_prompt,
                image_path=image_path,
                design_url=design_url or "",
                listing_title=listing["title"],
                listing_description=listing["description"],
                tags=listing["tags"],
                retail_price=retail_price,
                printful_product_id=str(printful_product["id"]) if printful_product else "",
                etsy_listing_id=str(etsy_listing["listing_id"]) if etsy_listing else "",
                mockup_url=mockup_url or "",
                status="draft" if etsy_listing else "design_only",
            )
            db.add(job)
            await db.commit()

        logger.info(
            "Publisher: pipeline complete for '%s' — Etsy listing %s",
            keyword,
            etsy_listing.get("listing_id") if etsy_listing else "N/A",
        )
        return True
