from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class NotificationType(str, enum.Enum):
    birth_alert = "birth_alert"
    vaccination_due = "vaccination_due"
    feed_stock_low = "feed_stock_low"
    missed_feeding = "missed_feeding"
    general = "general"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    related_animal_id = Column(Integer, ForeignKey("animals.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
    related_animal = relationship("Animal")
