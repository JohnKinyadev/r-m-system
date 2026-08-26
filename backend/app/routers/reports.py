from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.db.session import get_db
from app.db.models.animals import Animal, AnimalStatus
from app.db.models.health_logs import HealthLog
from app.db.models.feed_logs import FeedLog, FeedDistribution
from app.db.models.births import Birth
from app.db.models.mating_events import MatingEvent
from app.db.models.feed_types import FeedType
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/dashboard")
def dashboard_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total_animals = db.query(Animal).filter(Animal.status == AnimalStatus.active).count()
    sold = db.query(Animal).filter(Animal.status == AnimalStatus.sold).count()
    deceased = db.query(Animal).filter(Animal.status == AnimalStatus.deceased).count()
    total_births_this_month = (
        db.query(Birth)
        .filter(
            func.extract("month", Birth.birth_date) == date.today().month,
            func.extract("year", Birth.birth_date) == date.today().year,
        )
        .count()
    )
    upcoming_births = (
        db.query(MatingEvent)
        .filter(
            MatingEvent.expected_birth_date >= date.today(),
            MatingEvent.birth == None,
        )
        .count()
    )
    feed_stocks = db.query(FeedType).all()
    low_stock = [f.name for f in feed_stocks if f.current_stock <= f.low_stock_threshold]

    return {
        "active_animals": total_animals,
        "sold_animals": sold,
        "deceased_animals": deceased,
        "births_this_month": total_births_this_month,
        "upcoming_births": upcoming_births,
        "low_stock_feed_types": low_stock,
    }


@router.get("/herd-health")
def herd_health_summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    logs = db.query(HealthLog).all()
    by_type: dict = {}
    for log in logs:
        key = log.log_type.value
        by_type[key] = by_type.get(key, 0) + 1
    return {"total_logs": len(logs), "by_type": by_type}


@router.get("/feed-consumption")
def feed_consumption_report(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = (
        db.query(FeedDistribution.animal_id, func.sum(FeedDistribution.quantity).label("total"))
        .group_by(FeedDistribution.animal_id)
        .all()
    )
    return [{"animal_id": r.animal_id, "total_consumed": r.total} for r in rows]


@router.get("/birth-mortality")
def birth_mortality_report(db: Session = Depends(get_db), _=Depends(get_current_user)):
    births = db.query(Birth).count()
    deceased = db.query(Animal).filter(Animal.status == AnimalStatus.deceased).count()
    sold = db.query(Animal).filter(Animal.status == AnimalStatus.sold).count()
    return {"total_births_recorded": births, "deceased": deceased, "sold": sold}
