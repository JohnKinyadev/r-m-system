from pydantic import BaseModel
from app.schemas.users import UserRead


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class LoginRequest(BaseModel):
    email: str
    password: str
