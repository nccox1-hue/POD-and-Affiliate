"""
Scheduler for all automated pipelines.

Jobs:
  arbitrage_pipeline     — scan eBay sold listings, source, margin check, list. Every 24h.
  arbitrage_monitor      — price/stock check on active listings. Every 12h.
  ebay_order_poll        — check for paid eBay orders, fulfil, write tracking. Every 2h.
  digital_download       — generate and publish Etsy digital art listings. Every 56h (~3x/week).
  affiliate_writer       — write and publish one affiliate article. Every 56h (~3x/week).
"""
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings
from arbitrage.pipeline import ArbitragePipeline
from arbitrage.monitor import ArbitrageMonitor
from publisher.ebay_order_poller import EbayOrderPoller
from pod_digital.pipeline import DigitalDownloadPipeline
from pod_digital.template_pipeline import TemplatePipeline
from affiliate_writer.pipeline import AffiliateWriterPipeline
# Stream D (crypto) parked — risk/reward doesn't meet £1,000/month target without large capital
# from sandbox.funding_rate_scanner import scan_and_log
# from sandbox.position_manager import run_cycle

logger = logging.getLogger(__name__)


class ArbitrageScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.pipeline = ArbitragePipeline()
        self.monitor = ArbitrageMonitor()
        self.order_poller = EbayOrderPoller()
        self.digital = DigitalDownloadPipeline()
        self.templates = TemplatePipeline()
        self.affiliate = AffiliateWriterPipeline()

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
            next_run_time=None,
            max_instances=1,
        )
        self.scheduler.add_job(
            self.order_poller.poll_and_fulfil,
            IntervalTrigger(hours=2),
            id="ebay_order_poll",
            next_run_time=datetime.now(),
            max_instances=1,
        )
        self.scheduler.add_job(
            self.digital.run,
            IntervalTrigger(hours=56),
            id="digital_download",
            next_run_time=datetime.now(),
            max_instances=1,
        )
        self.scheduler.add_job(
            self.affiliate.run,
            IntervalTrigger(hours=24),
            id="affiliate_writer",
            next_run_time=datetime.now(),
            max_instances=1,
        )
        self.scheduler.add_job(
            self.templates.run,
            IntervalTrigger(hours=48),
            id="template_pipeline",
            next_run_time=datetime.now(),
            max_instances=1,
        )
        self.scheduler.start()
        logger.info(
            "Scheduler started — eBay arb every %dh | monitor 12h | orders 2h | "
            "digital downloads 56h | affiliate articles 56h",
            settings.scan_interval_hours,
        )

    def stop(self) -> None:
        self.scheduler.shutdown()
