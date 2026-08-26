from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.db.session import get_db
from app.db.models.health_logs import HealthLog
from app.db.models.animals import Animal
from app.db.models.users import User
from app.schemas.health import HealthLogCreate, HealthLogRead
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/animal/{animal_id}", response_model=List[HealthLogRead])
def list_health_logs(animal_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not db.query(Animal).filter(Animal.id == animal_id).first():
        raise HTTPException(status_code=404, detail="Animal not found")
    return db.query(HealthLog).filter(HealthLog.animal_id == animal_id).order_by(HealthLog.logged_at.desc()).all()


@router.post("", response_model=HealthLogRead, status_code=status.HTTP_201_CREATED)
def create_health_log(
    payload: HealthLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Animal).filter(Animal.id == payload.animal_id).first():
        raise HTTPException(status_code=404, detail="Animal not found")
    log = HealthLog(
        **payload.model_dump(exclude={"logged_at"}),
        logged_by=current_user.id,
        logged_at=payload.logged_at or datetime.now(timezone.utc),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_log(log_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    log = db.query(HealthLog).filter(HealthLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
