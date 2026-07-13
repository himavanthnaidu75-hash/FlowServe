from collections.abc import AsyncGenerator
from typing import AsyncContextManager

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


import subprocess
import sys


async def init_db() -> None:
    if settings.environment == "production":
        alembic_cfg = __file__.rsplit("app/database.py", 1)[0] + "alembic.ini"
        subprocess.run(
            [sys.executable, "-m", "alembic", "-c", alembic_cfg, "upgrade", "head"],
            cwd=__file__.rsplit("app/", 1)[0],
            check=True,
        )
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
