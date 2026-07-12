import uuid
from datetime import date, datetime
from datetime import timezone as _tz

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # draft | in_progress | review | completed
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    client = relationship("Client", back_populates="projects")
    time_entries = relationship(
        "TimeEntry", back_populates="project", cascade="all, delete-orphan"
    )
