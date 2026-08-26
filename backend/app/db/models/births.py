from sqlalchemy import Column, Integer, Date, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Birth(Base):
    __tablename__ = "births"

    id = Column(Integer, primary_key=True, index=True)
    mating_event_id = Column(Integer, ForeignKey("mating_events.id"), nullable=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)  # the mother
    birth_date = Column(Date, nullable=False)
    number_of_offspring = Column(Integer, nullable=False, default=1)
    notes = Column(Text, nullable=True)
    logged_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mating_event = relationship("MatingEvent", back_populates="birth")
    animal = relationship("Animal", back_populates="births")
    logger = relationship("User")
