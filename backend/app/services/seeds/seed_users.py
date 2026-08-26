from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.roles import Role
from app.db.models.users import User

_USERS = [
    {"full_name": "John Kamau", "email": "john.kamau@farm.ke", "role": "farm_worker"},
    {"full_name": "Mary Wanjiku", "email": "mary.wanjiku@farm.ke", "role": "farm_worker"},
    {"full_name": "Peter Ochieng", "email": "peter.ochieng@farm.ke", "role": "farm_worker"},
    {"full_name": "Grace Akinyi", "email": "grace.akinyi@farm.ke", "role": "farm_owner"},
    {"full_name": "David Mwangi", "email": "david.mwangi@farm.ke", "role": "farm_worker"},
]


def seed_users(db: Session) -> None:
    for u in _USERS:
        if db.query(User).filter(User.email == u["email"]).first():
            continue
        role = db.query(Role).filter(Role.name == u["role"]).first()
        db.add(User(
            full_name=u["full_name"],
            email=u["email"],
            hashed_password=hash_password("farmpass123"),
            role_id=role.id,
        ))
    db.commit()
