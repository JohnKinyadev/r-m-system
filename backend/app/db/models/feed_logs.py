from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class FeedLog(Base):
    """One log entry per feeding session (worker entry)."""
    __tablename__ = "feed_logs"

    id = Column(Integer, primary_key=True, index=True)
    feed_type_id = Column(Integer, ForeignKey("feed_types.id"), nullable=False)
    total_quantity = Column(Float, nullable=False)
    session_date = Column(DateTime(timezone=True), nullable=False)
    logged_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    feed_type = relationship("FeedType", back_populates="feed_logs")
    logger = relationship("User")
    distributions = relationship("FeedDistribution", back_populates="feed_log", cascade="all, delete-orphan")


class FeedDistribution(Base):
    """Auto-generated per-animal share from a FeedLog session."""
    __tablename__ = "feed_distributions"

    id = Column(Integer, primary_key=True, index=True)
    feed_log_id = Column(Integer, ForeignKey("feed_logs.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    quantity = Column(Float, nullable=False)

    feed_log = relationship("FeedLog", back_populates="distributions")
    animal = relationship("Animal", back_populates="feed_distributions")
