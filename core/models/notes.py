from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.models.base import Base


if TYPE_CHECKING:
    from core.models import User
    from core.models import Comment


class Note(Base):
    __tablename__ = "notes"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
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

    # Отношения
    user: Mapped["User"] = relationship(back_populates="notes")
    comments: Mapped["Comment"] = relationship(back_populates="note")
