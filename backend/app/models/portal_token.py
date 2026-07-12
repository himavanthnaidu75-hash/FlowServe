import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _token() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex


def _expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=365)


class PortalToken(Base):
    __tablename__ = "portal_tokens"

    token: Mapped[str] = mapped_column(String(72), primary_key=True, default=_token)
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_expiry, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
