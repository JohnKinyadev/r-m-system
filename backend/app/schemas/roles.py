from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: int

    model_config = {"from_attributes": True}
