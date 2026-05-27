"""
Arbitrage monitor — runs every 12h.

For each active listing:
  - Fetch current supplier price + stock
  - Recalculate margin at current price
  - If margin < 15%: end the eBay listing (unprofitable)
  - If stock = 0: pause the eBay listing (set quantity to 0)
  - If stock restored AND margin OK: resume (set quantity to 999)

The 15% end threshold is intentionally lower than the 25% listing threshold,
giving a buffer before we kill listings that are dipping slightly.
"""
import logging
from datetime import datetime

from sqlalchemy import select

from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import ActiveListing
from publisher.ebay_client import EbayClient
from scanner.avasam_sourcer import AvasamSourcer
from scanner.bigbuy_sourcer import BigBuySourcer
from scanner import margin_calculator as mc

logger = logging.getLogger(__name__)

END_MARGIN_THRESHOLD = 15.0     # end listing if margin falls below this %
PAUSE_STOCK_THRESHOLD = 0       # pause listing if stock at or below this


class ArbitrageMonitor:
    def __init__(self):
        self.ebay = EbayClient()
        self.avasam = AvasamSourcer()
        self.bigbuy = BigBuySourcer()

    async def run(self) -> None:
        """Check all active listings, pause/end as needed."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ActiveListing).where(ActiveListing.status == "active")
            )
            listings = result.scalars().all()

        if not listings:
            logger.info("Monitor: no active listings to check")
            return

        logger.info("Monitor: checking %d active listing(s)", len(listings))
        ended = paused = resumed = 0

        for listing in listings:
            try:
                action = await self._check_listing(listing)
                if action == "ended":
                    ended += 1
                elif action == "paused":
                    paused += 1
                elif action == "resumed":
                    resumed += 1
            except Exception as e:
                logger.error("Monitor error for listing %s: %s", listing.ebay_item_id, e)

        logger.info(
            "Monitor complete: %d ended | %d paused | %d resumed",
            ended, paused, resumed,
        )

    async def _check_listing(self, listing: ActiveListing) -> str:
        """Check one listing. Returns 'ended', 'paused', 'resumed', or 'ok'."""
        sourcer = self.avasam if listing.supplier == "avasam" else self.bigbuy
        current = await sourcer.get_product(listing.supplier_product_id)

        now = datetime.utcnow()

        # Supplier product no longer accessible — leave as-is, log warning
        if current is None:
            logger.warning(
                "Monitor: cannot fetch supplier data for listing %s (product_id=%s) — skipping",
                listing.ebay_item_id, listing.supplier_product_id,
            )
            await self._update_checked_at(listing.id, now)
            return "ok"

        wholesale = current["wholesale_price"]
        stock = current["stock_count"]
        calc = mc.calculate(listing.sell_price, wholesale)

        # Margin too low — end the listing
        if calc["margin_pct"] < END_MARGIN_THRESHOLD:
            logger.info(
                "Monitor: ending listing %s — margin dropped to %.1f%% (£%.2f wholesale, £%.2f sell)",
                listing.ebay_item_id, calc["margin_pct"], wholesale, listing.sell_price,
            )
            ok = await self.ebay.end_listing(listing.ebay_item_id, reason="NotAvailable")
            await self._update_status(listing.id, "ended" if ok else "active", wholesale, calc, now)
            return "ended" if ok else "ok"

        # Out of stock — pause
        if stock <= PAUSE_STOCK_THRESHOLD:
            if listing.status == "active":
                logger.info("Monitor: pausing listing %s — supplier out of stock", listing.ebay_item_id)
                ok = await self.ebay.revise_quantity(listing.ebay_item_id, 0)
                await self._update_status(listing.id, "paused" if ok else "active", wholesale, calc, now)
                return "paused" if ok else "ok"
        else:
            # Stock available — resume if currently paused
            if listing.status == "paused":
                logger.info("Monitor: resuming listing %s — stock restored (%d units)", listing.ebay_item_id, stock)
                ok = await self.ebay.revise_quantity(listing.ebay_item_id, 999)
                await self._update_status(listing.id, "active" if ok else "paused", wholesale, calc, now)
                return "resumed" if ok else "ok"

        # All good — just update checked_at and current margin
        await self._update_status(listing.id, listing.status, wholesale, calc, now)
        return "ok"

    async def _update_status(
        self,
        listing_id: int,
        status: str,
        wholesale: float,
        calc: dict,
        now: datetime,
    ) -> None:
        async with AsyncSessionLocal() as db:
            listing = await db.get(ActiveListing, listing_id)
            if listing:
                listing.status = status
                listing.wholesale_price_at_listing = wholesale
                listing.profit_gbp = calc["profit_gbp"]
                listing.margin_pct = calc["margin_pct"]
                listing.last_checked_at = now
                await db.commit()

    async def _update_checked_at(self, listing_id: int, now: datetime) -> None:
        async with AsyncSessionLocal() as db:
            listing = await db.get(ActiveListing, listing_id)
            if listing:
                listing.last_checked_at = now
                await db.commit()
