"""
Funding rate scanner for Stream D (crypto arb).
Fetches current funding rates from Bybit (and Binance for comparison).
Ranks opportunities by annualised yield and logs snapshots to the database.
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict

import ccxt

from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import FundingRateSnapshot

logger = logging.getLogger(__name__)

# Pairs to monitor — perp symbols in ccxt format
WATCH_SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "BNB/USDT:USDT",
    "SOL/USDT:USDT",
    "XRP/USDT:USDT",
    "DOGE/USDT:USDT",
    "ADA/USDT:USDT",
    "AVAX/USDT:USDT",
]

# Only open positions when annualised rate exceeds this threshold
MIN_ANNUALISED_PCT = 10.0

# Payments per day × days per year
ANNUALISE_FACTOR = 3 * 365


def _make_bybit(testnet: bool = True) -> ccxt.bybit:
    key = settings.bybit_testnet_api_key if testnet else settings.bybit_api_key
    secret = settings.bybit_testnet_api_secret if testnet else settings.bybit_api_secret
    exchange = ccxt.bybit({
        "apiKey": key,
        "secret": secret,
        "enableRateLimit": True,
        "options": {"defaultType": "swap"},
    })
    if testnet:
        exchange.set_sandbox_mode(True)
    return exchange


def _make_binance() -> ccxt.binance:
    return ccxt.binance({
        "enableRateLimit": True,
        "options": {"defaultType": "future"},
    })


def _annualise(rate: float) -> float:
    return rate * ANNUALISE_FACTOR * 100


async def fetch_bybit_rates(testnet: bool = True) -> List[Dict]:
    """Fetch current funding rates from Bybit for all watched symbols."""
    exchange = _make_bybit(testnet)
    results = []
    loop = asyncio.get_event_loop()

    for symbol in WATCH_SYMBOLS:
        try:
            data = await loop.run_in_executor(
                None, lambda s=symbol: exchange.fetch_funding_rate(s)
            )
            rate = float(data.get("fundingRate", 0))
            annualised = _annualise(rate)
            results.append({
                "exchange": "bybit",
                "symbol": symbol,
                "rate": rate,
                "annualised_pct": annualised,
                "next_funding_ts": data.get("fundingTimestamp"),
            })
            await asyncio.sleep(0.2)
        except Exception as e:
            logger.debug("Bybit rate fetch error for %s: %s", symbol, e)

    results.sort(key=lambda x: x["annualised_pct"], reverse=True)
    return results


async def fetch_binance_rates() -> List[Dict]:
    """Fetch Binance funding rates for comparison (public API — no auth needed)."""
    exchange = _make_binance()
    results = []
    loop = asyncio.get_event_loop()

    for symbol in WATCH_SYMBOLS:
        try:
            data = await loop.run_in_executor(
                None, lambda s=symbol: exchange.fetch_funding_rate(s)
            )
            rate = float(data.get("fundingRate", 0))
            results.append({
                "exchange": "binance",
                "symbol": symbol,
                "rate": rate,
                "annualised_pct": _annualise(rate),
                "next_funding_ts": data.get("fundingTimestamp"),
            })
            await asyncio.sleep(0.2)
        except Exception as e:
            logger.debug("Binance rate fetch error for %s: %s", symbol, e)

    return results


async def scan_and_log() -> List[Dict]:
    """
    Fetch rates from Bybit (+ Binance for comparison), log to DB, return top opportunities.
    Called by the scheduler every hour.
    """
    testnet = settings.bybit_testnet

    if not settings.bybit_testnet_api_key and not settings.bybit_api_key:
        logger.warning("Funding scanner: no Bybit API keys configured")
        return []

    logger.info("Funding scanner: fetching rates (testnet=%s)", testnet)

    bybit_rates = await fetch_bybit_rates(testnet)
    try:
        binance_rates = await fetch_binance_rates()
    except Exception as e:
        logger.warning("Binance rate fetch failed (non-critical): %s", e)
        binance_rates = []

    all_rates = bybit_rates + binance_rates

    # Log to database
    async with AsyncSessionLocal() as db:
        for r in all_rates:
            db.add(FundingRateSnapshot(
                exchange=r["exchange"],
                symbol=r["symbol"],
                rate=r["rate"],
                annualised_pct=r["annualised_pct"],
                next_funding_ts=r.get("next_funding_ts"),
            ))
        await db.commit()

    # Report top opportunities
    opportunities = [r for r in bybit_rates if r["annualised_pct"] >= MIN_ANNUALISED_PCT]

    if bybit_rates:
        logger.info("Funding scanner: top rates (Bybit):")
        for r in bybit_rates[:5]:
            logger.info(
                "  %s: %.4f%% rate → %.1f%% annualised",
                r["symbol"], r["rate"] * 100, r["annualised_pct"],
            )

    logger.info(
        "Funding scanner: %d opportunities above %.0f%% annualised threshold",
        len(opportunities), MIN_ANNUALISED_PCT,
    )
    return opportunities
