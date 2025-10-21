from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.models.base import Base


if TYPE_CHECKING:
    from core.models import User
    from core.models import Task
    from core.models import Note


class Comment(Base):
    __tablename__ = "comments"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Таймстемпы
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # Связи
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True
    )
    note_id: Mapped[int | None] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"), nullable=True
    )

    # Отношения
    user: Mapped["User"] = relationship(back_populates="comments")
    task: Mapped[Optional["Task"]] = relationship(back_populates="comments")
    note: Mapped[Optional["Note"]] = relationship(back_populates="comments")
