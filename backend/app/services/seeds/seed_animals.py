from datetime import date

from sqlalchemy.orm import Session

from app.db.models.animals import Animal, AnimalGender, AnimalStatus
from app.db.models.livestock_types import LivestockType


def _type(db: Session, name: str, breed: str) -> LivestockType:
    return db.query(LivestockType).filter(
        LivestockType.name == name, LivestockType.breed == breed
    ).first()


def _animal(db: Session, tag: str) -> Animal | None:
    return db.query(Animal).filter(Animal.tag_number == tag).first()


def seed_animals(db: Session) -> None:
    friesian = _type(db, "Cattle", "Friesian")
    angus = _type(db, "Cattle", "Angus")
    boer = _type(db, "Goat", "Boer")
    dorper = _type(db, "Sheep", "Dorper")
    lwhite = _type(db, "Pig", "Large White")

    # Insert parent animals first so offspring can reference their IDs
    parents = [
        # Friesian Cattle — 2 cows + 1 bull
        Animal(tag_number="KC001", name="Bella", livestock_type_id=friesian.id, gender=AnimalGender.female, date_of_birth=date(2019, 3, 15), status=AnimalStatus.active),
        Animal(tag_number="KC002", name="Daisy", livestock_type_id=friesian.id, gender=AnimalGender.female, date_of_birth=date(2020, 5, 20), status=AnimalStatus.active),
        Animal(tag_number="KC003", name="Thunder", livestock_type_id=friesian.id, gender=AnimalGender.male, date_of_birth=date(2018, 8, 10), status=AnimalStatus.active),
        # Angus Cattle — 1 bull + 2 cows
        Animal(tag_number="BC001", name="Max", livestock_type_id=angus.id, gender=AnimalGender.male, date_of_birth=date(2017, 11, 20), status=AnimalStatus.active),
        Animal(tag_number="BC002", name="Rosa", livestock_type_id=angus.id, gender=AnimalGender.female, date_of_birth=date(2019, 7, 15), status=AnimalStatus.active),
        Animal(tag_number="BC003", name="Cleo", livestock_type_id=angus.id, gender=AnimalGender.female, date_of_birth=date(2020, 2, 10), status=AnimalStatus.active),
        # Boer Goats — 1 buck + 2 does
        Animal(tag_number="GT001", name="Billy", livestock_type_id=boer.id, gender=AnimalGender.male, date_of_birth=date(2020, 1, 10), status=AnimalStatus.active),
        Animal(tag_number="GT002", name="Nanny", livestock_type_id=boer.id, gender=AnimalGender.female, date_of_birth=date(2021, 3, 22), status=AnimalStatus.active),
        Animal(tag_number="GT003", name="Spotty", livestock_type_id=boer.id, gender=AnimalGender.female, date_of_birth=date(2020, 11, 15), status=AnimalStatus.active),
        # Dorper Sheep — 1 ram + 2 ewes
        Animal(tag_number="SH001", name="Wooly", livestock_type_id=dorper.id, gender=AnimalGender.male, date_of_birth=date(2019, 5, 1), status=AnimalStatus.active),
        Animal(tag_number="SH002", name="Fluffy", livestock_type_id=dorper.id, gender=AnimalGender.female, date_of_birth=date(2020, 9, 18), status=AnimalStatus.active),
        Animal(tag_number="SH003", name="Curly", livestock_type_id=dorper.id, gender=AnimalGender.female, date_of_birth=date(2021, 3, 7), status=AnimalStatus.active),
        # Large White Pigs — 1 boar + 2 sows
        Animal(tag_number="PG001", name="Boar King", livestock_type_id=lwhite.id, gender=AnimalGender.male, date_of_birth=date(2020, 6, 12), status=AnimalStatus.active),
        Animal(tag_number="PG002", name="Pinky", livestock_type_id=lwhite.id, gender=AnimalGender.female, date_of_birth=date(2021, 1, 25), status=AnimalStatus.active),
        Animal(tag_number="PG003", name="Penny", livestock_type_id=lwhite.id, gender=AnimalGender.female, date_of_birth=date(2021, 8, 30), status=AnimalStatus.active),
    ]

    for a in parents:
        if not _animal(db, a.tag_number):
            db.add(a)
    db.commit()

    # Resolve parent IDs after commit
    bella = _animal(db, "KC001")
    daisy = _animal(db, "KC002")
    thunder = _animal(db, "KC003")
    max_ = _animal(db, "BC001")
    rosa = _animal(db, "BC002")
    cleo = _animal(db, "BC003")
    billy = _animal(db, "GT001")
    nanny = _animal(db, "GT002")
    spotty = _animal(db, "GT003")
    wooly = _animal(db, "SH001")
    fluffy = _animal(db, "SH002")
    curly = _animal(db, "SH003")
    boar = _animal(db, "PG001")
    pinky = _animal(db, "PG002")
    penny = _animal(db, "PG003")

    offspring = [
        # Friesian calves (mother/father linked)
        Animal(tag_number="KC004", name="Lila", livestock_type_id=friesian.id, gender=AnimalGender.female, date_of_birth=date(2022, 1, 5), mother_id=bella.id, father_id=thunder.id, status=AnimalStatus.active),
        Animal(tag_number="KC005", name="Spot", livestock_type_id=friesian.id, gender=AnimalGender.female, date_of_birth=date(2023, 4, 12), mother_id=daisy.id, father_id=thunder.id, status=AnimalStatus.active),
        # Angus calves
        Animal(tag_number="BC004", name="Junior", livestock_type_id=angus.id, gender=AnimalGender.male, date_of_birth=date(2022, 9, 8), mother_id=rosa.id, father_id=max_.id, status=AnimalStatus.active),
        Animal(tag_number="BC005", name="Sandy", livestock_type_id=angus.id, gender=AnimalGender.female, date_of_birth=date(2023, 6, 25), mother_id=cleo.id, father_id=max_.id, status=AnimalStatus.active),
        # Boer kids
        Animal(tag_number="GT004", name="Kid Bella", livestock_type_id=boer.id, gender=AnimalGender.female, date_of_birth=date(2023, 2, 28), mother_id=nanny.id, father_id=billy.id, status=AnimalStatus.active),
        Animal(tag_number="GT005", name="Kid Storm", livestock_type_id=boer.id, gender=AnimalGender.male, date_of_birth=date(2023, 7, 14), mother_id=spotty.id, father_id=billy.id, status=AnimalStatus.active),
        # Dorper lambs
        Animal(tag_number="SH004", name="Lamb Rose", livestock_type_id=dorper.id, gender=AnimalGender.female, date_of_birth=date(2023, 3, 15), mother_id=fluffy.id, father_id=wooly.id, status=AnimalStatus.active),
        Animal(tag_number="SH005", name="Lamb Duke", livestock_type_id=dorper.id, gender=AnimalGender.male, date_of_birth=date(2023, 8, 20), mother_id=curly.id, father_id=wooly.id, status=AnimalStatus.active),
        # Large White piglets
        Animal(tag_number="PG004", name="Piglet Rosie", livestock_type_id=lwhite.id, gender=AnimalGender.female, date_of_birth=date(2023, 4, 10), mother_id=pinky.id, father_id=boar.id, status=AnimalStatus.active),
        Animal(tag_number="PG005", name="Piglet Rex", livestock_type_id=lwhite.id, gender=AnimalGender.male, date_of_birth=date(2023, 9, 5), mother_id=penny.id, father_id=boar.id, status=AnimalStatus.active),
    ]

    for a in offspring:
        if not _animal(db, a.tag_number):
            db.add(a)
    db.commit()
