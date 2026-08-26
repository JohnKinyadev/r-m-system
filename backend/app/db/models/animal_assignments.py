from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AnimalAssignment(Base):
    """Links an animal to the worker(s) responsible for it."""
    __tablename__ = "animal_assignments"
    __table_args__ = (UniqueConstraint("animal_id", "worker_id", name="uq_animal_worker"),)

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    animal = relationship("Animal", back_populates="assignments")
    worker = relationship("User", back_populates="animal_assignments")
