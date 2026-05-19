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
    printful_product_id = Column(String(100))
    etsy_listing_id = Column(String(100))
    mockup_url = Column(String(500))
    status = Column(String(50), default="pending")  # pending, draft, active, failed
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
