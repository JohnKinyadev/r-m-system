from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class TenantStatus(str, enum.Enum):
    active = "active"
    notice = "notice"
    former = "former"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    national_id = Column(String(80), nullable=True)
    emergency_contact = Column(String(150), nullable=True)
    status = Column(Enum(TenantStatus), default=TenantStatus.active, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenancies = relationship("Tenancy", back_populates="tenant", cascade="all, delete-orphan")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="tenant")
