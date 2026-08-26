from pydantic import BaseModel, EmailStr, field_validator, field_serializer
from typing import Optional, List, Any
from datetime import datetime
from app.schemas.roles import RoleRead


class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role_id: int

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        from app.core.config import validate_password_strength
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        from app.core.config import validate_password_strength
        return validate_password_strength(v)


class UserRead(UserBase):
    id: int
    role: RoleRead
    is_active: bool
    created_at: datetime
    permissions: List[Any] = []

    model_config = {"from_attributes": True}

    @field_serializer("permissions")
    def serialize_permissions(self, perms: List[Any]) -> List[str]:
        from app.db.models.permissions import AVAILABLE_MODULES
        # Landlords always get all modules in the response
        role_name = self.role.name if self.role else ""
        if role_name == "landlord":
            return AVAILABLE_MODULES
        # Workers get the list of their granted modules
        result = []
        for p in perms:
            if isinstance(p, str):
                result.append(p)
            elif hasattr(p, "module"):
                result.append(p.module)
        return result
