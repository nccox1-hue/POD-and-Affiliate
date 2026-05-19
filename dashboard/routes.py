from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pathlib import Path

from database.db import get_db
from database.models import DesignJob, TrendRecord, SaleRecord

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

ETSY_FEES_RATE = 0.065 + 0.04  # 6.5% transaction + 4% payment processing
LISTING_FEE = 0.16


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    total_listings = (await db.execute(select(func.count(DesignJob.id)))).scalar() or 0
    active_listings = (await db.execute(
        select(func.count(DesignJob.id)).where(DesignJob.status == "active")
    )).scalar() or 0
    total_trends = (await db.execute(select(func.count(TrendRecord.id)))).scalar() or 0

    # Sales summary
    total_revenue = (await db.execute(select(func.sum(SaleRecord.sale_price)))).scalar() or 0.0
    total_profit = (await db.execute(select(func.sum(SaleRecord.profit)))).scalar() or 0.0
    total_sales = (await db.execute(select(func.count(SaleRecord.id)))).scalar() or 0

    # Recent jobs
    recent_jobs = (await db.execute(
        select(DesignJob).order_by(desc(DesignJob.created_at)).limit(20)
    )).scalars().all()

    # Theme breakdown
    theme_rows = (await db.execute(
        select(TrendRecord.theme, func.count(TrendRecord.id))
        .group_by(TrendRecord.theme)
    )).all()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "total_listings": total_listings,
        "active_listings": active_listings,
        "total_trends": total_trends,
        "total_revenue": f"£{total_revenue:.2f}",
        "total_profit": f"£{total_profit:.2f}",
        "total_sales": total_sales,
        "recent_jobs": recent_jobs,
        "theme_breakdown": [{"theme": r[0], "count": r[1]} for r in theme_rows],
    })


@router.get("/api/stats")
async def api_stats(db: AsyncSession = Depends(get_db)):
    return {
        "total_listings": (await db.execute(select(func.count(DesignJob.id)))).scalar(),
        "active_listings": (await db.execute(
            select(func.count(DesignJob.id)).where(DesignJob.status == "active")
        )).scalar(),
        "total_sales": (await db.execute(select(func.count(SaleRecord.id)))).scalar(),
        "total_profit": float((await db.execute(select(func.sum(SaleRecord.profit)))).scalar() or 0),
    }


@router.get("/api/jobs")
async def api_jobs(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(DesignJob).order_by(desc(DesignJob.created_at)).limit(50)
    )).scalars().all()
    return [
        {
            "id": r.id, "keyword": r.keyword, "theme": r.theme,
            "title": r.listing_title, "price": r.retail_price,
            "etsy_id": r.etsy_listing_id, "status": r.status,
            "created_at": str(r.created_at),
        }
        for r in rows
    ]
