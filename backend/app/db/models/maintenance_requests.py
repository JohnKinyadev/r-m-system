from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class MaintenanceStatus(str, enum.Enum):
    open = "open"
    assigned = "assigned"
    in_progress = "in_progress"
    resolved = "resolved"
    cancelled = "cancelled"


class MaintenancePriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.normal, nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.open, nullable=False)
    reported_date = Column(Date, nullable=False)
    resolved_date = Column(Date, nullable=True)
    cost = Column(Numeric(12, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="maintenance_requests")
    unit = relationship("Unit", back_populates="maintenance_requests")
    tenant = relationship("Tenant", back_populates="maintenance_requests")
    assigned_to = relationship("User")
