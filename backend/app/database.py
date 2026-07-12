from collections.abc import AsyncGenerator
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {}
if settings.environment == "production":
    connect_args = {"timeout": 10, "ssl": "require"}

engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    connect_args=connect_args,
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
        await conn.run_sync(Base.metadata.create_all)
