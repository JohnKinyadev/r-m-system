from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.feed_types import FeedType
from app.db.models.feed_logs import FeedLog, FeedDistribution
from app.db.models.feed_stock_arrivals import FeedStockArrival
from app.db.models.animals import Animal, AnimalStatus
from app.db.models.notifications import Notification, NotificationType
from app.db.models.users import User
from app.schemas.feed import (
    FeedTypeCreate, FeedTypeRead, FeedTypeUpdate,
    FeedLogCreate, FeedLogRead,
    FeedStockArrivalCreate, FeedStockArrivalRead,
)
from app.core.dependencies import get_current_user, require_owner

router = APIRouter(prefix="/api/feed", tags=["feed"])


# ── Feed Types ──────────────────────────────────────────────────────────────

@router.get("/types", response_model=List[FeedTypeRead])
def list_feed_types(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FeedType).all()


@router.post("/types", response_model=FeedTypeRead, status_code=status.HTTP_201_CREATED)
def create_feed_type(payload: FeedTypeCreate, db: Session = Depends(get_db), _=Depends(require_owner)):
    ft = FeedType(**payload.model_dump())
    db.add(ft)
    db.commit()
    db.refresh(ft)
    return ft


@router.patch("/types/{ft_id}", response_model=FeedTypeRead)
def update_feed_type(ft_id: int, payload: FeedTypeUpdate, db: Session = Depends(get_db), _=Depends(require_owner)):
    ft = db.query(FeedType).filter(FeedType.id == ft_id).first()
    if not ft:
        raise HTTPException(status_code=404, detail="Feed type not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(ft, field, value)
    db.commit()
    db.refresh(ft)
    return ft


# ── Stock Arrivals ──────────────────────────────────────────────────────────

@router.post("/stock-arrivals", response_model=FeedStockArrivalRead, status_code=status.HTTP_201_CREATED)
def log_stock_arrival(
    payload: FeedStockArrivalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ft = db.query(FeedType).filter(FeedType.id == payload.feed_type_id).first()
    if not ft:
        raise HTTPException(status_code=404, detail="Feed type not found")
    arrival = FeedStockArrival(**payload.model_dump(), logged_by=current_user.id)
    db.add(arrival)
    ft.current_stock += payload.quantity
    db.commit()
    db.refresh(arrival)
    return arrival


@router.get("/stock-arrivals", response_model=List[FeedStockArrivalRead])
def list_stock_arrivals(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FeedStockArrival).order_by(FeedStockArrival.arrived_at.desc()).all()


# ── Feeding Sessions ────────────────────────────────────────────────────────

@router.post("/logs", response_model=FeedLogRead, status_code=status.HTTP_201_CREATED)
def log_feeding_session(
    payload: FeedLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ft = db.query(FeedType).filter(FeedType.id == payload.feed_type_id).first()
    if not ft:
        raise HTTPException(status_code=404, detail="Feed type not found")

    active_animals = db.query(Animal).filter(Animal.status == AnimalStatus.active).all()
    if not active_animals:
        raise HTTPException(status_code=400, detail="No active animals to distribute feed to")

    feed_log = FeedLog(**payload.model_dump(), logged_by=current_user.id)
    db.add(feed_log)
    db.flush()

    per_animal = payload.total_quantity / len(active_animals)
    for animal in active_animals:
        db.add(FeedDistribution(feed_log_id=feed_log.id, animal_id=animal.id, quantity=round(per_animal, 4)))

    ft.current_stock = max(0, ft.current_stock - payload.total_quantity)

    if ft.current_stock <= ft.low_stock_threshold:
        owners = [u for u in db.query(User).all() if u.role.name == "farm_owner"]
        for owner in owners:
            db.add(Notification(
                user_id=owner.id,
                type=NotificationType.feed_stock_low,
                title=f"Low stock: {ft.name}",
                message=f"{ft.name} stock is at {ft.current_stock:.1f} {ft.unit}, below threshold of {ft.low_stock_threshold} {ft.unit}.",
            ))

    db.commit()
    db.refresh(feed_log)
    return feed_log


@router.get("/logs", response_model=List[FeedLogRead])
def list_feed_logs(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FeedLog).order_by(FeedLog.session_date.desc()).limit(100).all()
