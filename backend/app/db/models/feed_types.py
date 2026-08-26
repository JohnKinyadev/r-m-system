from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class FeedType(Base):
    __tablename__ = "feed_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True)
    unit = Column(String(50), nullable=False, default="kg")
    current_stock = Column(Float, nullable=False, default=0.0)
    low_stock_threshold = Column(Float, nullable=False, default=50.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    feed_logs = relationship("FeedLog", back_populates="feed_type")
    stock_arrivals = relationship("FeedStockArrival", back_populates="feed_type")
