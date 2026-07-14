import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # What happened
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # created | updated | deleted | sent | paid | overdue | milestone | comment | automated

    entity_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # client | project | proposal | invoice | lead | contract | time_entry

    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    entity_name: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Priority for notifications
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    # low | normal | high | urgent

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
