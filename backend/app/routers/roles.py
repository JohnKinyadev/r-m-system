from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.roles import Role
from app.schemas.roles import RoleRead
from app.core.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.get("", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Role).all()
