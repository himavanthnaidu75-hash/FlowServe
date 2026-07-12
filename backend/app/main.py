import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.database import Base, engine, init_db
from app.models import *
from app.routers import (
    auth,
    clients,
    dashboard,
    invoices,
    portal,
    projects,
    proposals,
    settings as settings_router,
    time_entries,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        logger.exception("init_db failed")
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="All-in-one service delivery platform for digital freelancers and agencies.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check (no auth)
@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}

@app.get("/debug/db")
async def debug_db():
    from urllib.parse import urlparse
    parsed = urlparse(settings.database_url)
    return {"scheme": parsed.scheme, "hostname": parsed.hostname, "port": parsed.port, "database": parsed.path.lstrip("/")}

@app.get("/debug/check")
async def debug_check():
    try:
        from app.database import engine
        async with engine.connect() as conn:
            result = await conn.execute(select(1))
            return {"db_ok": True, "result": result.scalar()}
    except Exception as e:
        return {"db_ok": False, "error": str(e)}


# API routes — all prefixed with /api
api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(clients.router, prefix=api_prefix)
app.include_router(projects.router, prefix=api_prefix)
app.include_router(proposals.router, prefix=api_prefix)
app.include_router(invoices.router, prefix=api_prefix)
app.include_router(time_entries.router, prefix=api_prefix)
app.include_router(settings_router.router, prefix=api_prefix)
app.include_router(portal.router, prefix=api_prefix)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
