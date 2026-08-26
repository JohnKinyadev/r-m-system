from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.core.security import decode_access_token
from app.db.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = (
        db.query(User)
        .options(joinedload(User.role), joinedload(User.permissions))
        .filter(User.id == int(user_id), User.is_active == True)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_owner(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name != "landlord":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Landlord access required")
    return current_user


def require_module(module: str):
    """Returns a FastAPI dependency that enforces per-module access for workers.
    Owners always pass; workers must have the module in their permissions."""
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name == "landlord":
            return current_user
        allowed = {p.module for p in current_user.permissions}
        if module not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access to '{module}' module not granted",
            )
        return current_user
    return _check
