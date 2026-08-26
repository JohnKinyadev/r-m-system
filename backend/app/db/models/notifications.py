from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class NotificationType(str, enum.Enum):
    rent_due = "rent_due"
    rent_overdue = "rent_overdue"
    payment_received = "payment_received"
    maintenance_update = "maintenance_update"
    lease_expiring = "lease_expiring"
    vacancy = "vacancy"
    general = "general"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    related_entity_type = Column(String(80), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
