from typing import List
from pydantic import BaseModel, EmailStr

# ---------------------------
# Pydantic Schemas
# ---------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: int
    scheme_id: int = None
    parent_id: int = None


class UserUpdateStatus(BaseModel):
    is_active: bool


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role_id: int
    scheme_id: int = None
    parent_id: int = None
    created_by: int = None
    is_active: bool

    class Config:
        from_attributes = True  