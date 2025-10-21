from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BaseNote(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    is_important: bool = False


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_important: bool = False


class NoteUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    is_important: Optional[bool] = None


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    is_important: bool = False
    created_at: datetime
    updated_at: datetime
