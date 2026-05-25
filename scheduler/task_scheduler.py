"""
Scheduler: scans for trends → generates designs → creates Etsy listings.
Runs once every SCAN_INTERVAL_HOURS (default: 24h).
"""
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import TrendRecord
from scraper.trend_aggregator import TrendAggregator
from publisher.publisher import Publisher
from publisher.ebay_order_poller import EbayOrderPoller

logger = logging.getLogger(__name__)


class PODScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.aggregator = TrendAggregator()
        self.publisher = Publisher()
        self.order_poller = EbayOrderPoller()

    def start(self):
        self.scheduler.add_job(
            self.run_pipeline,
            IntervalTrigger(hours=settings.scan_interval_hours),
            id="pod_pipeline",
            next_run_time=datetime.now(),
            max_instances=1,
        )
        self.scheduler.add_job(
            self.order_poller.poll_and_fulfil,
            IntervalTrigger(hours=2),
            id="ebay_order_poll",
            next_run_time=datetime.now(),
            max_instances=1,
        )
        self.scheduler.start()
        logger.info(
            "POD Scheduler started — pipeline every %dh, %d listings/cycle, themes: %s | eBay order poll every 2h",
            settings.scan_interval_hours,
            settings.listings_per_cycle,
            settings.themes,
        )

    def stop(self):
        self.scheduler.shutdown()

    async def run_pipeline(self):
        logger.info("=== POD Pipeline starting ===")

        # 1. Scan for trending design opportunities
        opportunities = await self.aggregator.scan()
        if not opportunities:
            logger.warning("No opportunities found this cycle")
            return

        # 2. Filter out already-used keywords
        async with AsyncSessionLocal() as db:
            used_result = await db.execute(
                select(TrendRecord.keyword).where(TrendRecord.used == True)
            )
            used_keywords = {row[0].lower() for row in used_result.all()}

        fresh = [o for o in opportunities if o["keyword"].lower() not in used_keywords]
        logger.info("Fresh opportunities: %d (filtered %d already used)", len(fresh), len(opportunities) - len(fresh))

        # 3. Process top N — rotate through product types across listings
        product_ids = settings.product_id_list or [71]
        successes = 0
        for i, opportunity in enumerate(fresh[:settings.listings_per_cycle]):
            opportunity["product_id"] = product_ids[i % len(product_ids)]
            if i > 0:
                await asyncio.sleep(10)  # avoid Gemini free-tier rate limit between listings
            try:
                # Save trend record
                async with AsyncSessionLocal() as db:
                    record = TrendRecord(
                        keyword=opportunity["keyword"],
                        source=opportunity.get("source", "unknown"),
                        theme=opportunity.get("theme", "general"),
                        score=opportunity.get("score", 0.0),
                        used=True,
                    )
                    db.add(record)
                    await db.commit()

                success = await self.publisher.run(opportunity)
                if success:
                    successes += 1
            except Exception as e:
                logger.error("Pipeline error for '%s': %s", opportunity.get("keyword"), e)

        logger.info("=== POD Pipeline complete: %d/%d listings created ===", successes, min(len(fresh), settings.listings_per_cycle))
