from sqlalchemy.orm import Session

from app.db.models.feed_types import FeedType

_FEED_TYPES = [
    {"name": "Rhodes Grass Hay", "unit": "kg", "current_stock": 650.0, "low_stock_threshold": 100.0},
    {"name": "Maize Silage", "unit": "kg", "current_stock": 1500.0, "low_stock_threshold": 200.0},
    {"name": "Dairy Meal (16% CP)", "unit": "kg", "current_stock": 420.0, "low_stock_threshold": 50.0},
    {"name": "Pig Grower Pellets", "unit": "kg", "current_stock": 180.0, "low_stock_threshold": 30.0},
    {"name": "Goat Mineral Pellets", "unit": "kg", "current_stock": 75.0, "low_stock_threshold": 20.0},
]


def seed_feed_types(db: Session) -> None:
    for ft in _FEED_TYPES:
        if not db.query(FeedType).filter(FeedType.name == ft["name"]).first():
            db.add(FeedType(**ft))
    db.commit()
