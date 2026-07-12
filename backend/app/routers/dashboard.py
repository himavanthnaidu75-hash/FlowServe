from datetime import date, timedelta
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.schemas.dashboard import DashboardStats, RevenuePoint

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = date.today()
    month_start = today.replace(day=1)

    active = await db.scalar(
        select(func.count(Project.id)).where(
            Project.user_id == user.id,
            Project.status.in_(["draft", "in_progress", "review"]),
        )
    )

    revenue = await db.scalar(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.user_id == user.id,
            Invoice.status == "paid",
            func.date(Invoice.paid_at) >= month_start,
        )
    )

    outstanding = await db.scalar(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.user_id == user.id,
            Invoice.status.in_(["pending", "overdue"]),
        )
    )

    tasks = await db.scalar(
        select(func.count(TimeEntry.id)).where(
            TimeEntry.user_id == user.id,
            func.date(TimeEntry.date) == today,
        )
    )

    return DashboardStats(
        active_projects=int(active or 0),
        revenue=float(revenue or 0),
        outstanding=float(outstanding or 0),
        tasks=int(tasks or 0),
    )


@router.get("/revenue", response_model=list[RevenuePoint])
async def get_revenue(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Last 6 months of revenue from paid invoices, summed by month."""
    today = date.today()
    start = (today.replace(day=1) - timedelta(days=5 * 31)).replace(day=1)

    rows = await db.execute(
        select(
            func.to_char(func.date_trunc("month", Invoice.paid_at), "YYYY-MM"),
            func.coalesce(func.sum(Invoice.amount), 0),
        )
        .where(
            Invoice.user_id == user.id,
            Invoice.status == "paid",
            Invoice.paid_at.isnot(None),
            func.date(Invoice.paid_at) >= start,
        )
        .group_by(
            func.date_trunc("month", Invoice.paid_at),
            func.to_char(func.date_trunc("month", Invoice.paid_at), "YYYY-MM"),
        )
        .order_by(func.date_trunc("month", Invoice.paid_at))
    )
    rows_pairs = rows.all()

    by_month: dict[str, float] = {m: float(a) for m, a in rows_pairs}

    out: list[RevenuePoint] = []
    cur = start
    for _ in range(6):
        key = cur.strftime("%Y-%m")
        label = cur.strftime("%b")
        out.append(RevenuePoint(month=label, revenue=by_month.get(key, 0.0)))
        cur = (cur.replace(day=1) + timedelta(days=31)).replace(day=1)

    return out
