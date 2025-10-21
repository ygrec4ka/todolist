from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime, func, ForeignKey

from core.models.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    jti: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    revoke: Mapped[bool] = mapped_column(default=False, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user = relationship("User", back_populates="refresh_tokens")
