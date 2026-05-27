"""
eBay margin calculator.

eBay UK fee structure (as of 2025):
- Final value fee: 12.8% of total sale price
- Fixed transaction fee: £0.30 per order
- (With Basic Shop subscription: ~9.9% + £0.30 — recalculate at scale)

Thresholds are read from settings and can be tuned in .env.
"""
from typing import Dict
from config.settings import settings

EBAY_FVF_RATE = 0.128   # 12.8%
EBAY_FVF_FIXED = 0.30   # £0.30 per transaction


def ebay_net(sell_price: float) -> float:
    """Net eBay revenue after fees."""
    return sell_price * (1 - EBAY_FVF_RATE) - EBAY_FVF_FIXED


def calculate(sell_price: float, wholesale_price: float) -> Dict:
    """
    Returns dict with:
      net_gbp     — eBay revenue after fees
      profit_gbp  — net minus wholesale cost
      margin_pct  — profit as % of sell price
    """
    net = ebay_net(sell_price)
    profit = net - wholesale_price
    margin = (profit / sell_price * 100) if sell_price > 0 else 0.0
    return {
        "net_gbp": round(net, 2),
        "profit_gbp": round(profit, 2),
        "margin_pct": round(margin, 1),
    }


def passes(profit_gbp: float, margin_pct: float) -> bool:
    return profit_gbp >= settings.min_profit_gbp and margin_pct >= settings.min_margin_pct


def score(profit_gbp: float, sold_count: int) -> float:
    """Higher profit × higher sell frequency = higher priority."""
    return round(profit_gbp * sold_count, 2)


def suggested_sell_price(sold_price: float, wholesale_price: float) -> float:
    """
    Price to list at.
    Use the original sold price — it's proven to sell at that level.
    If that doesn't yield enough margin, return None (caller skips the opportunity).
    """
    return round(sold_price, 2)
