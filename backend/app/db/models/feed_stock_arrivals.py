from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class FeedStockArrival(Base):
    __tablename__ = "feed_stock_arrivals"

    id = Column(Integer, primary_key=True, index=True)
    feed_type_id = Column(Integer, ForeignKey("feed_types.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    notes = Column(String(300), nullable=True)
    arrived_at = Column(DateTime(timezone=True), nullable=False)
    logged_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    feed_type = relationship("FeedType", back_populates="stock_arrivals")
    logger = relationship("User")
