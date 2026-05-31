"""
Delta-neutral position manager for funding rate arbitrage.

Strategy:
  - Buy X USDT of spot (long) + sell X USDT of perp (short)
  - Net price exposure = 0 (delta-neutral)
  - When funding rate > 0: shorts collect payments every 8h
  - Close when funding rate drops below exit threshold

Testnet only until explicitly switched to live.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict

import ccxt

from config.settings import settings
from database.db import AsyncSessionLocal
from database.models import FundingPosition
from sandbox.funding_rate_scanner import fetch_bybit_rates, MIN_ANNUALISED_PCT, _make_bybit

logger = logging.getLogger(__name__)

# Position sizing — conservative defaults for testnet
POSITION_SIZE_USDT = 100.0      # USDT per position (raise once live)
MAX_OPEN_POSITIONS = 3           # never more than 3 pairs at once
EXIT_ANNUALISED_THRESHOLD = 3.0  # close position if rate drops below this

# Perp symbol → spot symbol mapping
PERP_TO_SPOT = {
    "BTC/USDT:USDT": "BTC/USDT",
    "ETH/USDT:USDT": "ETH/USDT",
    "BNB/USDT:USDT": "BNB/USDT",
    "SOL/USDT:USDT": "SOL/USDT",
    "XRP/USDT:USDT": "XRP/USDT",
    "DOGE/USDT:USDT": "DOGE/USDT",
    "ADA/USDT:USDT": "ADA/USDT",
    "AVAX/USDT:USDT": "AVAX/USDT",
}


async def _open_position(exchange: ccxt.bybit, symbol: str, rate: float) -> Optional[Dict]:
    """
    Open a delta-neutral position: spot long + perp short.
    Returns order info dict or None on failure.
    """
    spot_symbol = PERP_TO_SPOT.get(symbol)
    if not spot_symbol:
        logger.error("No spot mapping for %s", symbol)
        return None

    loop = asyncio.get_event_loop()

    try:
        # Fetch current price to calculate order size
        ticker = await loop.run_in_executor(
            None, lambda: exchange.fetch_ticker(spot_symbol)
        )
        price = ticker["last"]
        if not price:
            logger.error("Could not fetch price for %s", spot_symbol)
            return None

        qty = round(POSITION_SIZE_USDT / price, 6)
        logger.info(
            "Opening position: %s | size=%.6f (%.2f USDT) @ %.4f | rate=%.4f%%",
            symbol, qty, POSITION_SIZE_USDT, price, rate * 100,
        )

        # Spot long — market buy
        spot_order = await loop.run_in_executor(
            None, lambda: exchange.create_order(
                spot_symbol, "market", "buy", qty,
                params={"category": "spot"}
            )
        )
        spot_id = spot_order.get("id", "")
        spot_price = spot_order.get("average") or price
        logger.info("Spot long placed: id=%s price=%.4f", spot_id, spot_price)

        # Perp short — market sell
        perp_order = await loop.run_in_executor(
            None, lambda: exchange.create_order(
                symbol, "market", "sell", qty,
                params={"category": "linear", "reduceOnly": False}
            )
        )
        perp_id = perp_order.get("id", "")
        perp_price = perp_order.get("average") or price
        logger.info("Perp short placed: id=%s price=%.4f", perp_id, perp_price)

        return {
            "spot_order_id": spot_id,
            "perp_order_id": perp_id,
            "spot_entry_price": float(spot_price),
            "perp_entry_price": float(perp_price),
            "size_usdt": POSITION_SIZE_USDT,
            "qty": qty,
        }

    except Exception as e:
        logger.error("Failed to open position for %s: %s", symbol, e)
        return None


async def _close_position(exchange: ccxt.bybit, position: FundingPosition) -> bool:
    """Close both legs of the position."""
    spot_symbol = PERP_TO_SPOT.get(position.symbol)
    if not spot_symbol:
        return False

    loop = asyncio.get_event_loop()
    try:
        # Calculate qty from size and entry price
        qty = round(position.size_usdt / position.spot_entry_price, 6) if position.spot_entry_price else 0
        if qty <= 0:
            logger.error("Cannot close position %s — qty is 0", position.id)
            return False

        # Close spot long — market sell
        await loop.run_in_executor(
            None, lambda: exchange.create_order(
                spot_symbol, "market", "sell", qty,
                params={"category": "spot"}
            )
        )

        # Close perp short — market buy (reduceOnly)
        await loop.run_in_executor(
            None, lambda: exchange.create_order(
                position.symbol, "market", "buy", qty,
                params={"category": "linear", "reduceOnly": True}
            )
        )

        logger.info("Position %s closed: %s", position.id, position.symbol)
        return True

    except Exception as e:
        logger.error("Failed to close position %s: %s", position.id, e)
        return False


async def run_cycle() -> None:
    """
    Main position management cycle:
    1. Fetch current rates
    2. Close positions where rate has dropped below exit threshold
    3. Open new positions where rate is attractive and we have capacity
    """
    testnet = settings.bybit_testnet
    key = settings.bybit_testnet_api_key if testnet else settings.bybit_api_key
    if not key:
        logger.warning("Position manager: no Bybit API key — skipping")
        return

    exchange = _make_bybit(testnet)
    loop = asyncio.get_event_loop()

    # Fetch current rates
    current_rates = await fetch_bybit_rates(testnet)
    rate_map = {r["symbol"]: r for r in current_rates}

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(FundingPosition).where(FundingPosition.status == "open")
        )
        open_positions = result.scalars().all()

        # 1. Close positions where rate has dropped
        for pos in open_positions:
            current = rate_map.get(pos.symbol, {})
            current_ann = current.get("annualised_pct", 0)

            if current_ann < EXIT_ANNUALISED_THRESHOLD:
                logger.info(
                    "Closing position %s: rate %.1f%% below exit threshold %.1f%%",
                    pos.symbol, current_ann, EXIT_ANNUALISED_THRESHOLD,
                )
                closed = await _close_position(exchange, pos)
                if closed:
                    pos.status = "closed"
                    pos.closed_at = datetime.utcnow()
                    pos.close_reason = f"rate dropped to {current_ann:.1f}%"

        await db.commit()

        # 2. Open new positions if we have capacity
        open_count = sum(1 for p in open_positions if p.status == "open")
        open_symbols = {p.symbol for p in open_positions if p.status == "open"}
        capacity = MAX_OPEN_POSITIONS - open_count

        if capacity <= 0:
            logger.info("Position manager: at max capacity (%d positions)", MAX_OPEN_POSITIONS)
            return

        for rate_data in current_rates:
            if capacity <= 0:
                break
            symbol = rate_data["symbol"]
            ann = rate_data["annualised_pct"]

            if symbol in open_symbols:
                continue
            if ann < MIN_ANNUALISED_PCT:
                break  # list is sorted, no point checking further

            order = await _open_position(exchange, symbol, rate_data["rate"])
            if order:
                db.add(FundingPosition(
                    exchange="bybit",
                    symbol=symbol,
                    spot_symbol=PERP_TO_SPOT.get(symbol, ""),
                    size_usdt=order["size_usdt"],
                    entry_rate=rate_data["rate"],
                    spot_order_id=order["spot_order_id"],
                    perp_order_id=order["perp_order_id"],
                    spot_entry_price=order["spot_entry_price"],
                    perp_entry_price=order["perp_entry_price"],
                ))
                open_symbols.add(symbol)
                capacity -= 1
                await asyncio.sleep(2)

        await db.commit()

    logger.info("Position manager cycle complete. Open positions: %d", MAX_OPEN_POSITIONS - capacity)
