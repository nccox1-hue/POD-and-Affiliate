"""
eBay order poller — checks for paid eBay orders and submits them to Avasam/BigBuy for fulfilment.
Also polls for tracking updates and writes them back to eBay via CompleteSale.
Runs on a schedule (every 2h).
"""
import logging
from datetime import datetime

from sqlalchemy import select

from database.db import AsyncSessionLocal
from database.models import ActiveListing, FulfillmentOrder
from publisher.ebay_client import EbayClient
from scanner.avasam_sourcer import AvasamSourcer
from scanner.bigbuy_sourcer import BigBuySourcer

logger = logging.getLogger(__name__)


class EbayOrderPoller:
    def __init__(self):
        self.ebay = EbayClient()
        self.avasam = AvasamSourcer()
        self.bigbuy = BigBuySourcer()

    async def poll_and_fulfil(self) -> None:
        logger.info("eBay order poller: checking for paid orders")

        orders = await self.ebay.get_paid_orders(days_back=30)
        if not orders:
            logger.info("eBay order poller: no new orders")
        else:
            await self._process_new_orders(orders)

        await self._submit_tracking_updates()

    async def _process_new_orders(self, orders: list) -> None:
        processed = 0
        for order in orders:
            order_id = order.get("order_id", "")
            item_id = order.get("item_id", "")
            if not order_id or not item_id:
                continue

            # Skip orders already in the DB
            async with AsyncSessionLocal() as db:
                existing = await db.execute(
                    select(FulfillmentOrder).where(FulfillmentOrder.ebay_order_id == order_id)
                )
                if existing.scalar_one_or_none():
                    continue

                # Find the ActiveListing this order belongs to
                listing_result = await db.execute(
                    select(ActiveListing).where(ActiveListing.ebay_item_id == item_id)
                )
                listing = listing_result.scalar_one_or_none()

            if not listing:
                logger.warning("Order %s: no ActiveListing for ItemID %s — skipping", order_id, item_id)
                continue

            recipient = {
                "name":         order.get("name", ""),
                "address1":     order.get("address1", ""),
                "address2":     order.get("address2", "") or "",
                "city":         order.get("city", ""),
                "state":        order.get("state", "") or "",
                "postcode":     order.get("zip", ""),
                "country_code": order.get("country_code", "GB"),
            }

            sourcer = self.avasam if listing.supplier == "avasam" else self.bigbuy
            supplier_order_id = await sourcer.place_order(
                supplier_sku=listing.supplier_sku,
                quantity=order.get("quantity", 1),
                recipient=recipient,
            )

            status = "submitted" if supplier_order_id else "failed"
            async with AsyncSessionLocal() as db:
                record = FulfillmentOrder(
                    ebay_order_id=order_id,
                    ebay_item_id=item_id,
                    active_listing_id=listing.id,
                    supplier=listing.supplier,
                    supplier_order_id=supplier_order_id or "",
                    quantity=order.get("quantity", 1),
                    buyer_name=order.get("name", ""),
                    address1=order.get("address1", ""),
                    address2=order.get("address2", "") or "",
                    city=order.get("city", ""),
                    state=order.get("state", "") or "",
                    postcode=order.get("zip", ""),
                    country_code=order.get("country_code", "GB"),
                    status=status,
                )
                db.add(record)
                await db.commit()

            if supplier_order_id:
                logger.info(
                    "Order %s fulfilled via %s — supplier_order_id=%s (item=%s)",
                    order_id, listing.supplier.upper(), supplier_order_id, item_id,
                )
                processed += 1
            else:
                logger.error("Order %s: %s fulfilment failed (item=%s)", order_id, listing.supplier.upper(), item_id)

        logger.info("eBay order poller: %d new order(s) submitted to supplier", processed)

    async def _submit_tracking_updates(self) -> None:
        """Check submitted orders for supplier tracking and post back to eBay."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(FulfillmentOrder).where(
                    FulfillmentOrder.status == "submitted",
                    FulfillmentOrder.supplier_order_id != "",
                    FulfillmentOrder.tracking_submitted == False,
                )
            )
            pending = result.scalars().all()

        updates = 0
        for order in pending:
            sourcer = self.avasam if order.supplier == "avasam" else self.bigbuy
            tracking = await sourcer.get_order_tracking(order.supplier_order_id)
            if not tracking or not tracking.get("tracking_number"):
                continue

            ok = await self.ebay.mark_shipped(
                order.ebay_order_id,
                tracking["tracking_number"],
                tracking.get("carrier", ""),
            )

            async with AsyncSessionLocal() as db:
                db_order = await db.get(FulfillmentOrder, order.id)
                if db_order:
                    db_order.tracking_number = tracking["tracking_number"]
                    db_order.carrier = tracking.get("carrier", "")
                    db_order.tracking_submitted = ok
                    db_order.status = "shipped" if ok else "tracking_failed"
                    await db.commit()

            if ok:
                updates += 1
                logger.info("Order %s: tracking %s submitted to eBay", order.ebay_order_id, tracking["tracking_number"])

        if updates:
            logger.info("eBay order poller: %d tracking update(s) written back to eBay", updates)
