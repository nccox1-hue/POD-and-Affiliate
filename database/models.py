from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class DesignJob(Base):
    __tablename__ = "design_jobs"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255))
    theme = Column(String(100))
    design_prompt = Column(Text)
    image_path = Column(String(500))
    design_url = Column(String(500))
    listing_title = Column(String(500))
    listing_description = Column(Text)
    tags = Column(JSON)
    retail_price = Column(Float)
    product_id = Column(Integer)
    printful_product_id = Column(String(100))
    etsy_listing_id = Column(String(100))
    ebay_item_id = Column(String(100))
    mockup_url = Column(String(500))
    status = Column(String(50), default="pending")  # pending, draft, active, failed
    created_at = Column(DateTime, default=datetime.utcnow)


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
    status = Column(String(50), default="pending")  # pending, submitted, failed
    created_at = Column(DateTime, default=datetime.utcnow)


class TrendRecord(Base):
    __tablename__ = "trend_records"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255))
    source = Column(String(50))
    theme = Column(String(100))
    score = Column(Float)
    used = Column(Boolean, default=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)


class SaleRecord(Base):
    __tablename__ = "sale_records"

    id = Column(Integer, primary_key=True, index=True)
    etsy_listing_id = Column(String(100))
    etsy_order_id = Column(String(100))
    product_name = Column(String(255))
    sale_price = Column(Float)
    printful_cost = Column(Float)
    profit = Column(Float)
    sold_at = Column(DateTime, default=datetime.utcnow)
