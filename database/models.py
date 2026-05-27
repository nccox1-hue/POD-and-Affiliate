from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class ScannedItem(Base):
    """A sold eBay listing found by the scanner."""
    __tablename__ = "scanned_items"

    id = Column(Integer, primary_key=True, index=True)
    ebay_item_id = Column(String(100), index=True)
    title = Column(String(500))
    category_id = Column(String(20))
    category_name = Column(String(100))
    sold_price = Column(Float)
    sold_count = Column(Integer, default=1)  # occurrences in scan window
    image_url = Column(String(500))
    scanned_at = Column(DateTime, default=datetime.utcnow)


class ArbitrageOpportunity(Base):
    """A scanned item matched to a supplier with margin passing filter."""
    __tablename__ = "arbitrage_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    scanned_item_id = Column(Integer, index=True)  # FK to ScannedItem.id
    supplier = Column(String(20))                  # "avasam" | "bigbuy"
    supplier_product_id = Column(String(100))
    supplier_sku = Column(String(100))
    wholesale_price = Column(Float)
    suggested_sell_price = Column(Float)
    profit_gbp = Column(Float)
    margin_pct = Column(Float)
    stock_count = Column(Integer, default=0)
    supplier_title = Column(String(500))
    supplier_image_url = Column(String(500))
    score = Column(Float, default=0.0)             # profit × sold_count
    status = Column(String(20), default="pending") # pending | listed | skipped
    created_at = Column(DateTime, default=datetime.utcnow)


class ActiveListing(Base):
    """Our live eBay listing for an arbitrage opportunity."""
    __tablename__ = "active_listings"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, index=True)   # FK to ArbitrageOpportunity.id
    ebay_item_id = Column(String(100), unique=True, index=True)
    supplier = Column(String(20))
    supplier_product_id = Column(String(100))
    supplier_sku = Column(String(100))
    sell_price = Column(Float)
    wholesale_price_at_listing = Column(Float)
    profit_gbp = Column(Float)
    margin_pct = Column(Float)
    status = Column(String(20), default="active")  # active | paused | ended
    listed_at = Column(DateTime, default=datetime.utcnow)
    last_checked_at = Column(DateTime, nullable=True)


class FulfillmentOrder(Base):
    """Order placed with Avasam/BigBuy to fulfil an eBay sale."""
    __tablename__ = "fulfillment_orders"

    id = Column(Integer, primary_key=True, index=True)
    ebay_order_id = Column(String(100), unique=True, index=True)
    ebay_item_id = Column(String(100))
    active_listing_id = Column(Integer, index=True)  # FK to ActiveListing.id
    supplier = Column(String(20))
    supplier_order_id = Column(String(100), default="")
    quantity = Column(Integer, default=1)
    buyer_name = Column(String(255))
    address1 = Column(String(255))
    address2 = Column(String(255), default="")
    city = Column(String(100))
    state = Column(String(100), default="")
    postcode = Column(String(20))
    country_code = Column(String(5), default="GB")
    tracking_number = Column(String(100), default="")
    carrier = Column(String(100), default="")
    tracking_submitted = Column(Boolean, default=False)
    status = Column(String(50), default="pending")  # pending | submitted | shipped | failed | tracking_failed
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Kept for backwards compatibility with existing DB rows ────────────────────
# These tables are no longer written to by the active pipeline.

class EbayOrder(Base):
    __tablename__ = "ebay_orders"

    id = Column(Integer, primary_key=True, index=True)
    ebay_order_id = Column(String(100), unique=True, index=True)
    ebay_item_id = Column(String(100))
    size = Column(String(20))
    quantity = Column(Integer, default=1)
    buyer_name = Column(String(255))
    address1 = Column(String(255))
    address2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postcode = Column(String(20))
    country_code = Column(String(5))
    printful_order_id = Column(String(100))
    tracking_number = Column(String(100), default="")
    carrier = Column(String(100), default="")
    tracking_submitted = Column(Boolean, default=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
