"""
FastAPI dashboard routes — arbitrage bot seller overview.
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from database.db import get_db
import json, os
from database.models import ScannedItem, ArbitrageOpportunity, ActiveListing, FulfillmentOrder, FundingRateSnapshot, FundingPosition, DigitalListing

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
logger = logging.getLogger(__name__)


def _listing_dict(l: ActiveListing) -> Dict[str, Any]:
    return {
        "id": l.id,
        "ebay_item_id": l.ebay_item_id,
        "supplier": l.supplier.upper(),
        "sell_price": l.sell_price,
        "wholesale_price": l.wholesale_price_at_listing,
        "profit_gbp": l.profit_gbp,
        "margin_pct": l.margin_pct,
        "status": l.status,
        "listed_at": l.listed_at,
        "last_checked_at": l.last_checked_at,
    }


def _order_dict(o: FulfillmentOrder) -> Dict[str, Any]:
    return {
        "id": o.id,
        "ebay_order_id": o.ebay_order_id,
        "ebay_item_id": o.ebay_item_id,
        "supplier": o.supplier.upper() if o.supplier else "—",
        "buyer_name": o.buyer_name or "",
        "quantity": o.quantity,
        "status": o.status,
        "supplier_order_id": o.supplier_order_id or "",
        "tracking_number": o.tracking_number or "",
        "carrier": o.carrier or "",
        "tracking_submitted": o.tracking_submitted,
        "created_at": o.created_at,
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    total_active = (await db.execute(
        select(func.count(ActiveListing.id)).where(ActiveListing.status == "active")
    )).scalar() or 0

    total_paused = (await db.execute(
        select(func.count(ActiveListing.id)).where(ActiveListing.status == "paused")
    )).scalar() or 0

    total_ended = (await db.execute(
        select(func.count(ActiveListing.id)).where(ActiveListing.status == "ended")
    )).scalar() or 0

    total_scanned = (await db.execute(select(func.count(ScannedItem.id)))).scalar() or 0

    total_orders = (await db.execute(select(func.count(FulfillmentOrder.id)))).scalar() or 0

    shipped_orders = (await db.execute(
        select(func.count(FulfillmentOrder.id)).where(FulfillmentOrder.status == "shipped")
    )).scalar() or 0

    est_profit = float((await db.execute(
        select(func.sum(ActiveListing.profit_gbp)).where(ActiveListing.status == "active")
    )).scalar() or 0.0)

    avg_margin = float((await db.execute(
        select(func.avg(ActiveListing.margin_pct)).where(ActiveListing.status == "active")
    )).scalar() or 0.0)

    recent_listings = (await db.execute(
        select(ActiveListing).order_by(desc(ActiveListing.listed_at)).limit(40)
    )).scalars().all()

    recent_orders = (await db.execute(
        select(FulfillmentOrder).order_by(desc(FulfillmentOrder.created_at)).limit(10)
    )).scalars().all()

    recent_scanned = (await db.execute(
        select(ScannedItem).order_by(desc(ScannedItem.scanned_at)).limit(10)
    )).scalars().all()

    last_scan = (await db.execute(select(func.max(ScannedItem.scanned_at)))).scalar()
    last_listed = (await db.execute(select(func.max(ActiveListing.listed_at)))).scalar()

    supplier_breakdown = (await db.execute(
        select(ActiveListing.supplier, func.count(ActiveListing.id))
        .where(ActiveListing.status == "active")
        .group_by(ActiveListing.supplier)
    )).all()

    # Stream A: Etsy digital downloads
    digital_active = (await db.execute(
        select(func.count(DigitalListing.id)).where(DigitalListing.status == "active")
    )).scalar() or 0

    digital_total = (await db.execute(
        select(func.count(DigitalListing.id))
    )).scalar() or 0

    recent_digital = (await db.execute(
        select(DigitalListing).order_by(desc(DigitalListing.created_at)).limit(10)
    )).scalars().all()

    # Stream B: Affiliate articles
    keyword_queue_path = os.path.join("data", "affiliate_keywords.json")
    articles_published = 0
    articles_pending = 0
    if os.path.exists(keyword_queue_path):
        with open(keyword_queue_path) as f:
            kq = json.load(f)
        articles_published = len(kq.get("published", []))
        articles_pending = len(kq.get("pending", []))

    # Crypto parked — removed from dashboard

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "total_active": total_active,
            "total_paused": total_paused,
            "total_ended": total_ended,
            "total_scanned": total_scanned,
            "total_orders": total_orders,
            "shipped_orders": shipped_orders,
            "est_profit": f"£{est_profit:.2f}",
            "avg_margin": f"{avg_margin:.1f}%",
            "recent_listings": [_listing_dict(l) for l in recent_listings],
            "recent_orders": [_order_dict(o) for o in recent_orders],
            "recent_scanned": [
                {
                    "title": s.title,
                    "category_name": s.category_name,
                    "sold_price": s.sold_price,
                    "sold_count": s.sold_count,
                    "scanned_at": s.scanned_at,
                }
                for s in recent_scanned
            ],
            "supplier_breakdown": [
                {"supplier": r[0].upper() if r[0] else "?", "count": r[1]}
                for r in supplier_breakdown
            ],
            "last_scan": last_scan.strftime("%d/%m/%Y %H:%M") if last_scan else None,
            "last_listed": last_listed.strftime("%d/%m/%Y %H:%M") if last_listed else None,
            "funding_rates": [
                {
                    "symbol": r.symbol,
                    "annualised_pct": f"{r.annualised_pct:.1f}%",
                    "rate": f"{r.rate:.6f}",
                    "recorded_at": r.recorded_at.strftime("%H:%M"),
                }
                for r in latest_rates
            ],
            "open_positions": [
                {
                    "symbol": p.symbol,
                    "size_usdt": f"${p.size_usdt:.0f}",
                    "entry_rate": f"{p.entry_rate:.4f}",
                    "funding_collected": f"${p.funding_collected:.4f}",
                    "opened_at": p.opened_at.strftime("%d/%m %H:%M"),
                }
                for p in open_positions
            ],
            "total_funding_collected": f"${total_funding_collected:.4f}",
            # Stream A
            "digital_active": digital_active,
            "digital_total": digital_total,
            "recent_digital": [
                {
                    "etsy_listing_id": d.etsy_listing_id,
                    "title": d.title,
                    "theme": d.theme,
                    "price_gbp": d.price_gbp,
                    "files_uploaded": d.files_uploaded,
                    "created_at": d.created_at.strftime("%d/%m %H:%M"),
                }
                for d in recent_digital
            ],
            # Stream B
            "articles_published": articles_published,
            "articles_pending": articles_pending,
        },
    )


@router.post("/run-now")
async def run_now(request: Request):
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler:
        asyncio.create_task(scheduler.pipeline.run())
    return RedirectResponse(url="/", status_code=303)


@router.get("/api/stats")
async def api_stats(db: AsyncSession = Depends(get_db)):
    return {
        "active_listings": (await db.execute(
            select(func.count(ActiveListing.id)).where(ActiveListing.status == "active")
        )).scalar(),
        "paused_listings": (await db.execute(
            select(func.count(ActiveListing.id)).where(ActiveListing.status == "paused")
        )).scalar(),
        "total_orders": (await db.execute(select(func.count(FulfillmentOrder.id)))).scalar(),
        "shipped_orders": (await db.execute(
            select(func.count(FulfillmentOrder.id)).where(FulfillmentOrder.status == "shipped")
        )).scalar(),
        "est_profit_active": float((await db.execute(
            select(func.sum(ActiveListing.profit_gbp)).where(ActiveListing.status == "active")
        )).scalar() or 0),
    }
