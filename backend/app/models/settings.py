import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    company_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    brand_color: Mapped[str] = mapped_column(String(20), default="#fbbf24", nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="usd", nullable=False)
    timezone: Mapped[str] = mapped_column(String(40), default="UTC", nullable=False)

    # JSON: list of toggles {email_updates: bool, sms_updates: bool, ...}
    notifications: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {
            "email_updates": True,
            "sms_updates": False,
            "payment_reminders": True,
            "weekly_summary": True,
        },
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
