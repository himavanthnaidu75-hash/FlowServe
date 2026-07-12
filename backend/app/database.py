from collections.abc import AsyncGenerator
from typing import AsyncContextManager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_size=5,
    max_overflow=2,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables. Use Alembic for real migrations in production."""
    async with engine.begin() as conn:
        try:
            await conn.run_sync(lambda c: c.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(120) NOT NULL DEFAULT ''")))
        except Exception:
            pass
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn))
