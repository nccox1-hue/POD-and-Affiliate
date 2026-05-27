"""Arbitrage Bot — entrypoint."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from rich.logging import RichHandler

from config.settings import settings
from database.db import init_db
from dashboard.routes import router as dashboard_router
from scheduler.task_scheduler import ArbitrageScheduler

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)

os.makedirs("data", exist_ok=True)

scheduler: ArbitrageScheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    await init_db()
    scheduler = ArbitrageScheduler()
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    scheduler.stop()


app = FastAPI(title="Arbitrage Bot", lifespan=lifespan)
app.include_router(dashboard_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=False)
