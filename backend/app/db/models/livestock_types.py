from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LivestockType(Base):
    __tablename__ = "livestock_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    breed = Column(String(100), nullable=True)
    gestation_period_days = Column(Integer, nullable=True)
    average_lifespan_years = Column(Float, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User")
    vaccine_schedules = relationship("VaccineSchedule", back_populates="livestock_type", cascade="all, delete-orphan")
    animals = relationship("Animal", back_populates="livestock_type")
