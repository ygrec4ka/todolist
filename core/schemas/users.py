from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=50)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
