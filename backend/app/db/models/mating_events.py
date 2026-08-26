from sqlalchemy import Column, Integer, Date, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class MatingEvent(Base):
    __tablename__ = "mating_events"

    id = Column(Integer, primary_key=True, index=True)
    female_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    male_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    mating_date = Column(Date, nullable=False)
    expected_birth_date = Column(Date, nullable=True)  # auto-computed on insert
    notes = Column(Text, nullable=True)
    logged_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    female = relationship("Animal", foreign_keys=[female_id], back_populates="mating_events_as_female")
    male = relationship("Animal", foreign_keys=[male_id], back_populates="mating_events_as_male")
    logger = relationship("User")
    birth = relationship("Birth", back_populates="mating_event", uselist=False)
