import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.middleware import RateLimitMiddleware
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
    leads,
    notifications,
    contracts,
    analytics,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        logger.exception("init_db failed")

    # Start automation engine in background
    import asyncio
    from app.services.automation_engine import run_automations

    async def automation_loop():
        while True:
            try:
                await run_automations()
            except Exception:
                logger.exception("Automation run failed")
            await asyncio.sleep(3600)  # Run every hour

    task = asyncio.create_task(automation_loop())
    yield
    task.cancel()


app = FastAPI(
    title=settings.app_name,
    version="3.0.0",
    description="AI-powered freelancing platform with automation, lead discovery, and smart insights.",
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

if settings.environment == "production":
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "env": settings.environment, "version": "3.0.0"}


# Core API routes
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

# New automation & intelligence routes
app.include_router(leads.router, prefix=api_prefix)
app.include_router(notifications.router, prefix=api_prefix)
app.include_router(contracts.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Client Management",
            "Project Tracking",
            "Proposal Generation",
            "Invoice Automation",
            "Time Tracking",
            "Lead Discovery & Scoring",
            "Revenue Forecasting",
            "Smart Notifications",
            "Contract Generation",
            "Business Analytics",
        ],
    }
