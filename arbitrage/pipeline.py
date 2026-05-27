"""
Arbitrage pipeline.

Each cycle:
  1. Scan eBay sold listings (Finding API)
  2. For each result, search Avasam then BigBuy for a matching product
  3. Run margin check — skip if profit < £3 or margin < 25%
  4. Claude writes eBay title + description
  5. Create eBay listing (reuses existing ebay_client)
  6. Save ScannedItem → ArbitrageOpportunity → ActiveListing to DB

When neither supplier key is set, steps 2-5 are skipped and only ScannedItems are saved
(so you can see what the scanner is finding while waiting for API keys).
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import ScannedItem, ArbitrageOpportunity, ActiveListing
from generator.listing_generator import generate_listing
from publisher.ebay_client import EbayClient
from scanner.ebay_sold_scanner import EbaySoldScanner
from scanner.avasam_sourcer import AvasamSourcer
from scanner.bigbuy_sourcer import BigBuySourcer
from scanner import margin_calculator as mc

logger = logging.getLogger(__name__)

# eBay category → product has size variations (clothing) or not
_HAS_SIZES: Dict[str, bool] = {
    "11450": True,   # Clothing
    "15724": True,   # Men's T-Shirts
    "15691": True,   # Women's T-Shirts
}


class ArbitragePipeline:
    def __init__(self):
        self.scanner = EbaySoldScanner()
        self.avasam = AvasamSourcer()
        self.bigbuy = BigBuySourcer()
        self.ebay = EbayClient()

    async def run(self) -> int:
        """
        Run one pipeline cycle. Returns number of listings created.
        Scans 3× listings_per_cycle to allow for match failures.
        """
        scan_target = settings.listings_per_cycle * 3
        logger.info("Arbitrage pipeline: scanning eBay sold listings (target %d opportunities)", settings.listings_per_cycle)

        sold_items = await self.scanner.scan_all()
        if not sold_items:
            logger.warning("Arbitrage pipeline: scanner returned no results")
            return 0

        # Save all scanned items to DB (useful for inspection even without supplier keys)
        await self._save_scanned_items(sold_items[:scan_target])

        # Skip listing creation if no supplier keys are configured
        if not settings.avasam_api_key and not settings.bigbuy_api_key:
            logger.info(
                "Arbitrage pipeline: no supplier keys set — %d scanned items saved, no listings created. "
                "Add AVASAM_API_KEY or BIGBUY_API_KEY to .env to enable listing creation.",
                len(sold_items[:scan_target]),
            )
            return 0

        listings_created = 0
        for item in sold_items[:scan_target]:
            if listings_created >= settings.listings_per_cycle:
                break
            try:
                created = await self._process_item(item)
                if created:
                    listings_created += 1
                    await asyncio.sleep(3)  # avoid hammering eBay listing API
            except Exception as e:
                logger.error("Pipeline error for '%s': %s", item.get("title", "?")[:60], e)

        logger.info("Arbitrage pipeline: %d listing(s) created this cycle", listings_created)
        return listings_created

    async def _process_item(self, item: Dict) -> bool:
        """Match one scanned item to a supplier, check margin, create listing."""
        title = item["title"]
        sold_price = item["sold_price"]

        # 1. Try to source — Avasam first, BigBuy fallback
        match = await self._source(title)
        if not match:
            logger.debug("No supplier match for '%s'", title[:60])
            return False

        # 2. Margin check at the original sold price
        calc = mc.calculate(sold_price, match["wholesale_price"])
        if not mc.passes(calc["profit_gbp"], calc["margin_pct"]):
            logger.debug(
                "Margin fail for '%s': profit=£%.2f margin=%.1f%%",
                title[:50], calc["profit_gbp"], calc["margin_pct"],
            )
            return False

        sell_price = mc.suggested_sell_price(sold_price, match["wholesale_price"])
        opp_score = mc.score(calc["profit_gbp"], item["sold_count"])

        # 3. Check not already listed
        if await self._already_listed(match["supplier_product_id"], match["supplier"]):
            logger.debug("Already listed: supplier_product_id=%s", match["supplier_product_id"])
            return False

        # 4. Generate listing copy
        listing = await generate_listing(title, match["supplier_title"])
        listing_title = listing["title"][:80]
        listing_description = listing["description"]

        # 5. Create eBay listing
        has_sizes = _HAS_SIZES.get(item["category_id"], False)
        ebay_item_id = await self.ebay.create_listing(
            title=listing_title,
            description=listing_description,
            price_gbp=sell_price,
            image_url=match["supplier_image_url"] or "",
            category_id=item["category_id"],
            has_sizes=has_sizes,
            item_specifics=None,
        )
        if not ebay_item_id:
            logger.error("eBay listing creation failed for '%s'", title[:60])
            return False

        # 6. Save opportunity + active listing to DB
        async with AsyncSessionLocal() as db:
            opp = ArbitrageOpportunity(
                scanned_item_id=item.get("_db_id"),
                supplier=match["supplier"],
                supplier_product_id=match["supplier_product_id"],
                supplier_sku=match["supplier_sku"],
                wholesale_price=match["wholesale_price"],
                suggested_sell_price=sell_price,
                profit_gbp=calc["profit_gbp"],
                margin_pct=calc["margin_pct"],
                stock_count=match["stock_count"],
                supplier_title=match["supplier_title"],
                supplier_image_url=match["supplier_image_url"],
                score=opp_score,
                status="listed",
            )
            db.add(opp)
            await db.flush()

            active = ActiveListing(
                opportunity_id=opp.id,
                ebay_item_id=ebay_item_id,
                supplier=match["supplier"],
                supplier_product_id=match["supplier_product_id"],
                supplier_sku=match["supplier_sku"],
                sell_price=sell_price,
                wholesale_price_at_listing=match["wholesale_price"],
                profit_gbp=calc["profit_gbp"],
                margin_pct=calc["margin_pct"],
                status="active",
            )
            db.add(active)
            await db.commit()

        logger.info(
            "Listed: '%s' | eBay %s | %s @ £%.2f wholesale → £%.2f sell | profit £%.2f (%.1f%%)",
            listing_title[:55],
            ebay_item_id,
            match["supplier"].upper(),
            match["wholesale_price"],
            sell_price,
            calc["profit_gbp"],
            calc["margin_pct"],
        )
        return True

    async def _source(self, title: str) -> Optional[Dict]:
        """Try Avasam, then BigBuy. Return first match found."""
        match = await self.avasam.search(title)
        if match:
            return match
        match = await self.bigbuy.search(title)
        return match

    async def _already_listed(self, supplier_product_id: str, supplier: str) -> bool:
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ActiveListing).where(
                    ActiveListing.supplier_product_id == supplier_product_id,
                    ActiveListing.supplier == supplier,
                    ActiveListing.status == "active",
                )
            )
            return result.scalar_one_or_none() is not None

    async def _save_scanned_items(self, items: list) -> None:
        """Persist scanned eBay items to DB and attach _db_id to each dict."""
        async with AsyncSessionLocal() as db:
            for item in items:
                record = ScannedItem(
                    ebay_item_id=item.get("ebay_item_id", ""),
                    title=item.get("title", ""),
                    category_id=item.get("category_id", ""),
                    category_name=item.get("category_name", ""),
                    sold_price=item.get("sold_price", 0.0),
                    sold_count=item.get("sold_count", 1),
                    image_url=item.get("image_url", ""),
                )
                db.add(record)
                await db.flush()
                item["_db_id"] = record.id
            await db.commit()
