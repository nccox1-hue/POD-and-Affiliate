"""
Orchestrates the full pipeline for one design opportunity:
trend keyword → design prompt → image → listing copy → Printful product → Etsy + eBay listings
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import settings
from config.themes import THEME_CATALOGUE
from generator.design_generator import generate_design, build_design_prompt, build_pollinations_url
from generator.listing_generator import generate_listing
from publisher.printful_client import PrintfulClient, PRODUCT_VARIANTS
from publisher.etsy_client import EtsyClient
from publisher.ebay_client import EbayClient
from database.db import AsyncSessionLocal
from database.models import DesignJob

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self):
        self.printful = PrintfulClient()
        self.etsy = EtsyClient()
        self.ebay = EbayClient()

    async def run(self, opportunity: Dict[str, Any]) -> bool:
        """Full pipeline for one design opportunity. Returns True on success."""
        keyword = opportunity["keyword"]
        theme = opportunity.get("theme", "funny")
        product_id = opportunity.get("product_id", settings.product_id_list[0] if settings.product_id_list else 71)
        product_meta = PRODUCT_VARIANTS.get(product_id, PRODUCT_VARIANTS[71])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_kw = "".join(c for c in keyword[:30] if c.isalnum() or c in " _").replace(" ", "_")
        filename = f"{safe_kw}_{timestamp}"

        logger.info(
            "Publisher: starting pipeline for '%s' (theme: %s, product: %s)",
            keyword, theme, product_meta["name"],
        )

        # 1. Generate AI image prompt
        design_prompt = await build_design_prompt(keyword, theme)
        logger.info("Design prompt: %s", design_prompt)

        # 2. Generate design image locally
        image_path = await generate_design(design_prompt, filename)
        if not image_path:
            logger.error("Design generation failed for '%s'", keyword)
            return False

        # 3. Upload design to Printful via Pollinations URL (avoids large base64 payload)
        pollinations_url = build_pollinations_url(design_prompt)
        design_url = await self.printful.upload_design_file(image_path, f"{filename}.png", source_url=pollinations_url)

        # 4. Generate listing copy — brief pause before 2nd Gemini call
        await asyncio.sleep(15)
        listing = await generate_listing(keyword, theme, product_meta["name"])

        # 5. Calculate retail price from per-product base cost
        base_cost = product_meta.get("base_cost_gbp", 10.0)
        retail_price = round(base_cost * settings.price_multiplier, 2)

        # 6. Create Printful sync product
        printful_product = None
        if design_url and settings.printful_api_key:
            printful_product = await self.printful.create_sync_product(
                name=listing["title"][:140],
                description=listing["description"],
                design_url=design_url,
                product_id=product_id,
                retail_price=str(retail_price),
            )

        # 7. Generate product mockup (t-shirt/hoodie worn by model, mug on desk, etc.)
        # Use the short URL here — Printful's mockup renderer fails on long URLs
        mockup_url = None
        mockup_path = None
        if design_url and settings.printful_api_key:
            variants = product_meta.get("variants", [])
            mockup_short_url = build_pollinations_url(design_prompt, short=True)
            mockup_url = await self.printful.get_mockup_url(product_id, variants[:1], mockup_short_url)
            if mockup_url:
                mockup_path = str(Path(image_path).parent / f"{filename}_mockup.jpg")
                ok = await self.printful.download_mockup(mockup_url, mockup_path)
                if not ok:
                    mockup_path = None

        # 8. Create Etsy draft listing
        etsy_listing = None
        if settings.etsy_access_token:
            etsy_listing = await self.etsy.create_draft_listing(
                title=listing["title"],
                description=listing["description"],
                price_gbp=retail_price,
                tags=listing["tags"],
                materials=listing.get("materials", ["Cotton"]),
                taxonomy_id=product_meta.get("etsy_taxonomy_id", 559),
            )

            if etsy_listing:
                listing_id = etsy_listing["listing_id"]
                # Primary image: mockup (product on model/surface) if available, else raw design
                primary_image = mockup_path if mockup_path else image_path
                await self.etsy.upload_listing_image(listing_id, primary_image, rank=1)
                # Secondary image: raw design (so buyers can see the graphic clearly)
                if mockup_path:
                    await self.etsy.upload_listing_image(listing_id, image_path, rank=2)

        # 9. Create eBay listing
        # Use mockup URL for eBay image (Printful S3 URL is short); fall back to short Pollinations URL
        ebay_item_id = None
        if settings.ebay_access_token:
            ebay_image_url = mockup_url or build_pollinations_url(design_prompt, short=True)
            ebay_item_id = await self.ebay.create_listing(
                title=listing["title"],
                description=listing["description"],
                price_gbp=retail_price,
                image_url=ebay_image_url,
                category_id=product_meta.get("ebay_category_id", "15687"),
                has_sizes=product_meta.get("has_sizes", True),
                item_specifics=product_meta.get("ebay_item_specifics"),
            )

        # 10. Save to database
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
                product_id=product_id,
                printful_product_id=str(printful_product["id"]) if printful_product else "",
                etsy_listing_id=str(etsy_listing["listing_id"]) if etsy_listing else "",
                ebay_item_id=str(ebay_item_id) if ebay_item_id else "",
                mockup_url=mockup_url or "",
                status="draft" if etsy_listing else "design_only",
            )
            db.add(job)
            await db.commit()

        logger.info(
            "Publisher: pipeline complete for '%s' [%s] — Etsy %s | eBay %s | mockup %s",
            keyword,
            product_meta["name"],
            etsy_listing.get("listing_id") if etsy_listing else "N/A",
            ebay_item_id or "N/A",
            "yes" if mockup_url else "no",
        )
        return True
