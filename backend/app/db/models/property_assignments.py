from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PropertyAssignment(Base):
    __tablename__ = "property_assignments"
    __table_args__ = (UniqueConstraint("property_id", "caretaker_id", name="uq_property_caretaker"),)

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    caretaker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="assignments")
    caretaker = relationship("User", back_populates="property_assignments")
