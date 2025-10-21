from datetime import datetime
from typing import TYPE_CHECKING, Optional

from core.models.base import Base

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.sql import func


if TYPE_CHECKING:
    from core.models import Task
    from core.models import Note
    from core.models import Comment
    from core.models import RefreshToken


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # Таймстемпы
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Отношения
    tasks: Mapped[Optional[list["Task"]]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notes: Mapped[Optional[list["Note"]]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    comments: Mapped[Optional[list["Comment"]]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
