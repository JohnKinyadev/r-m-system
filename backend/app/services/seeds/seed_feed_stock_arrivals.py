from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.feed_stock_arrivals import FeedStockArrival
from app.db.models.feed_types import FeedType
from app.db.models.roles import Role
from app.db.models.users import User


def _feed(db: Session, name: str) -> FeedType:
    return db.query(FeedType).filter(FeedType.name == name).first()


def seed_feed_stock_arrivals(db: Session) -> None:
    owner = db.query(User).join(User.role).filter(Role.name == "farm_owner").first()
    mary = db.query(User).filter(User.email == "mary.wanjiku@farm.ke").first()

    arrivals = [
        {
            "feed": "Rhodes Grass Hay",
            "quantity": 500.0,
            "notes": "Purchased from Meru Feeds Ltd — bulk dry season stock",
            "arrived_at": datetime(2024, 1, 10, 10, 0, tzinfo=timezone.utc),
            "logged_by": owner.id,
        },
        {
            "feed": "Maize Silage",
            "quantity": 1000.0,
            "notes": "Bulk delivery from Nakuru farm supplier",
            "arrived_at": datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc),
            "logged_by": owner.id,
        },
        {
            "feed": "Dairy Meal (16% CP)",
            "quantity": 300.0,
            "notes": "Monthly dairy meal restock from agro-vet",
            "arrived_at": datetime(2024, 2, 1, 11, 0, tzinfo=timezone.utc),
            "logged_by": mary.id,
        },
        {
            "feed": "Pig Grower Pellets",
            "quantity": 150.0,
            "notes": "Restocked from Kisumu agro-vet store",
            "arrived_at": datetime(2024, 2, 10, 8, 0, tzinfo=timezone.utc),
            "logged_by": mary.id,
        },
        {
            "feed": "Goat Mineral Pellets",
            "quantity": 60.0,
            "notes": "Supplementary mineral feed for breeding does",
            "arrived_at": datetime(2024, 2, 20, 14, 0, tzinfo=timezone.utc),
            "logged_by": owner.id,
        },
        {
            "feed": "Rhodes Grass Hay",
            "quantity": 300.0,
            "notes": "Top-up delivery ahead of long rains — reduced grazing expected",
            "arrived_at": datetime(2024, 3, 5, 10, 30, tzinfo=timezone.utc),
            "logged_by": mary.id,
        },
    ]

    for a in arrivals:
        feed = _feed(db, a["feed"])
        exists = db.query(FeedStockArrival).filter(
            FeedStockArrival.feed_type_id == feed.id,
            FeedStockArrival.arrived_at == a["arrived_at"],
        ).first()
        if not exists:
            db.add(FeedStockArrival(
                feed_type_id=feed.id,
                quantity=a["quantity"],
                notes=a["notes"],
                arrived_at=a["arrived_at"],
                logged_by=a["logged_by"],
            ))
    db.commit()
