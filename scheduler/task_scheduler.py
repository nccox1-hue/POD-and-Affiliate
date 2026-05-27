"""
Scheduler for the arbitrage bot.

Jobs:
  arbitrage_pipeline  — scan eBay sold listings, source, margin check, list. Every SCAN_INTERVAL_HOURS (default 24h).
  arbitrage_monitor   — price/stock check on active listings, end/pause as needed. Every 12h.
  ebay_order_poll     — check for paid eBay orders, submit to supplier, write back tracking. Every 2h.
"""
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings
from arbitrage.pipeline import ArbitragePipeline
from arbitrage.monitor import ArbitrageMonitor
from publisher.ebay_order_poller import EbayOrderPoller

logger = logging.getLogger(__name__)


class ArbitrageScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.pipeline = ArbitragePipeline()
        self.monitor = ArbitrageMonitor()
        self.order_poller = EbayOrderPoller()

    def start(self) -> None:
        self.scheduler.add_job(
            self.pipeline.run,
            IntervalTrigger(hours=settings.scan_interval_hours),
            id="arbitrage_pipeline",
            next_run_time=datetime.now(),
            max_instances=1,
        )
        self.scheduler.add_job(
            self.monitor.run,
            IntervalTrigger(hours=12),
            id="arbitrage_monitor",
            next_run_time=None,  # don't run immediately on startup — pipeline runs first
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
            "Arbitrage scheduler started — pipeline every %dh | monitor every 12h | order poll every 2h",
            settings.scan_interval_hours,
        )

    def stop(self) -> None:
        self.scheduler.shutdown()
