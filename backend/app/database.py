from collections.abc import AsyncGenerator
from typing import AsyncContextManager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.base import Base
from app.config import settings


is_pg = "asyncpg" in settings.database_url
pg_kwargs = {"pool_size": 5, "max_overflow": 2, "connect_args": {"ssl": "require"}} if is_pg else {}

engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    **pg_kwargs,
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
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.columns "
                "WHERE table_name='contracts' AND column_name='total_value' "
                "AND data_type='character varying') THEN DROP TABLE contracts CASCADE; END IF; END $$"
            )
        )
        await conn.run_sync(Base.metadata.create_all)
