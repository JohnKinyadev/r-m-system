from datetime import date

from sqlalchemy.orm import Session

from app.db.models.animals import Animal
from app.db.models.mating_events import MatingEvent
from app.db.models.roles import Role
from app.db.models.users import User


def _animal(db: Session, tag: str) -> Animal:
    return db.query(Animal).filter(Animal.tag_number == tag).first()


def seed_mating_events(db: Session) -> None:
    owner = db.query(User).join(User.role).filter(Role.name == "farm_owner").first()

    # (female_tag, male_tag, mating_date, expected_birth_date, notes)
    # expected_birth = mating_date + gestation (Friesian 280d, Angus 285d, Boer 150d, Dorper 147d, Large White 114d)
    events = [
        ("KC001", "KC003", date(2021, 4, 1),  date(2022, 1, 5),  "Bella × Thunder — first mating"),
        ("KC002", "KC003", date(2022, 6, 6),  date(2023, 3, 13), "Daisy × Thunder — first mating"),
        ("BC002", "BC001", date(2021, 12, 1), date(2022, 9, 12), "Rosa × Max — first mating"),
        ("BC003", "BC001", date(2022, 9, 13), date(2023, 6, 25), "Cleo × Max — first mating"),
        ("GT002", "GT001", date(2022, 9, 30), date(2023, 2, 27), "Nanny × Billy — expecting twins"),
        ("GT003", "GT001", date(2023, 2, 13), date(2023, 7, 13), "Spotty × Billy — first mating"),
        ("SH002", "SH001", date(2022, 10, 19), date(2023, 3, 15), "Fluffy × Wooly — first mating"),
        ("SH003", "SH001", date(2023, 3, 25), date(2023, 8, 19), "Curly × Wooly — first mating"),
        ("PG002", "PG001", date(2022, 12, 17), date(2023, 4, 10), "Pinky × Boar King — first litter"),
        ("PG003", "PG001", date(2023, 5, 14), date(2023, 9, 5),  "Penny × Boar King — first litter"),
    ]

    for female_tag, male_tag, mating_date, expected_birth, notes in events:
        female = _animal(db, female_tag)
        male = _animal(db, male_tag)
        exists = db.query(MatingEvent).filter(
            MatingEvent.female_id == female.id,
            MatingEvent.male_id == male.id,
            MatingEvent.mating_date == mating_date,
        ).first()
        if not exists:
            db.add(MatingEvent(
                female_id=female.id,
                male_id=male.id,
                mating_date=mating_date,
                expected_birth_date=expected_birth,
                notes=notes,
                logged_by=owner.id,
            ))
    db.commit()
