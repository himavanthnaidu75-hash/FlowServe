from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, init_db
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup in dev. Use Alembic in production.
    if settings.environment == "development":
        await init_db()
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
