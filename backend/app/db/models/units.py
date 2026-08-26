from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class UnitStatus(str, enum.Enum):
    vacant = "vacant"
    reserved = "reserved"
    occupied = "occupied"
    notice_given = "notice_given"
    maintenance = "maintenance"
    unavailable = "unavailable"


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (UniqueConstraint("property_id", "unit_number", name="uq_property_unit"),)

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    unit_number = Column(String(50), nullable=False)
    unit_type = Column(String(80), nullable=False)
    floor = Column(String(50), nullable=True)
    bedrooms = Column(Integer, default=1, nullable=False)
    bathrooms = Column(Integer, default=1, nullable=False)
    monthly_rent = Column(Numeric(12, 2), nullable=False)
    deposit_amount = Column(Numeric(12, 2), default=0, nullable=False)
    rent_due_day = Column(Integer, default=5, nullable=False)
    status = Column(Enum(UnitStatus), default=UnitStatus.vacant, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="units")
    tenancies = relationship("Tenancy", back_populates="unit", cascade="all, delete-orphan")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="unit")


class UnitRentHistory(Base):
    __tablename__ = "unit_rent_history"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    rent_amount = Column(Numeric(12, 2), nullable=False)
    effective_from = Column(DateTime(timezone=True), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
