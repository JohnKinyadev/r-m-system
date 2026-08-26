from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class PropertyStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    property_type = Column(String(80), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.active, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    units = relationship("Unit", back_populates="property", cascade="all, delete-orphan")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")
    expenses = relationship("Expense", back_populates="property")
    assignments = relationship("PropertyAssignment", back_populates="property", cascade="all, delete-orphan")
