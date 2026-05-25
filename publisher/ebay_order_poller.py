"""
eBay order poller — checks for paid eBay orders and submits them to Printful for fulfilment.
Runs on a schedule (every 2h). Tracks processed orders in the ebay_orders table.
"""
import logging
from sqlalchemy import select

from database.db import AsyncSessionLocal
from database.models import DesignJob, EbayOrder
from publisher.ebay_client import EbayClient, SIZE_TO_VARIANT
from publisher.printful_client import PrintfulClient

logger = logging.getLogger(__name__)


class EbayOrderPoller:
    def __init__(self):
        self.ebay = EbayClient()
        self.printful = PrintfulClient()

    async def poll_and_fulfil(self):
        logger.info("eBay order poller: checking for paid orders")

        orders = await self.ebay.get_paid_orders(days_back=30)
        if not orders:
            logger.info("eBay order poller: no orders found")
            return

        processed = 0
        for order in orders:
            order_id = order.get("order_id", "")
            item_id = order.get("item_id", "")

            if not order_id or not item_id:
                continue

            async with AsyncSessionLocal() as db:
                # Skip if already processed
                existing = await db.execute(
                    select(EbayOrder).where(EbayOrder.ebay_order_id == order_id)
                )
                if existing.scalar_one_or_none():
                    continue

                # Look up the design job to get design URL and retail price
                job_result = await db.execute(
                    select(DesignJob).where(DesignJob.ebay_item_id == item_id)
                )
                job = job_result.scalar_one_or_none()

            if not job:
                logger.warning("eBay order %s: no DesignJob found for ItemID %s — skipping", order_id, item_id)
                continue

            size = order.get("size", "M")
            variant_id = SIZE_TO_VARIANT.get(size, SIZE_TO_VARIANT["M"])
            if size not in SIZE_TO_VARIANT:
                logger.warning("eBay order %s: unknown size '%s', defaulting to M", order_id, size)

            recipient = {
                "name":     order.get("name", ""),
                "address1": order.get("address1", ""),
                "address2": order.get("address2", "") or "",
                "city":     order.get("city", ""),
                "state_code": order.get("state", "") or "",
                "country_code": order.get("country_code", "GB"),
                "zip":      order.get("zip", ""),
            }

            printful_order_id = await self.printful.create_order(
                recipient=recipient,
                variant_id=variant_id,
                quantity=order.get("quantity", 1),
                design_url=job.design_url,
                retail_price=str(job.retail_price),
            )

            status = "submitted" if printful_order_id else "failed"

            async with AsyncSessionLocal() as db:
                record = EbayOrder(
                    ebay_order_id=order_id,
                    ebay_item_id=item_id,
                    size=size,
                    quantity=order.get("quantity", 1),
                    buyer_name=order.get("name", ""),
                    address1=order.get("address1", ""),
                    address2=order.get("address2", "") or "",
                    city=order.get("city", ""),
                    state=order.get("state", "") or "",
                    postcode=order.get("zip", ""),
                    country_code=order.get("country_code", "GB"),
                    printful_order_id=printful_order_id or "",
                    status=status,
                )
                db.add(record)
                await db.commit()

            if printful_order_id:
                logger.info(
                    "eBay order %s fulfilled — Printful order id=%s (ItemID=%s size=%s)",
                    order_id, printful_order_id, item_id, size,
                )
                processed += 1
            else:
                logger.error("eBay order %s: Printful submission failed (ItemID=%s)", order_id, item_id)

        logger.info("eBay order poller: %d new order(s) submitted to Printful", processed)
