from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BaseComment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    task_id: Optional[int] = None
    note_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    created_at: datetime
    updated_at: datetime
