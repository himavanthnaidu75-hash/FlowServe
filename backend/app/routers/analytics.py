from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.time_entry import TimeEntry
from app.models.lead import Lead
from app.models.user import User
from app.services.revenue_forecast import forecast_revenue

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def analytics_overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Comprehensive business analytics overview."""
    from datetime import date, timedelta
    from sqlalchemy import extract

    today = date.today()
    month_start = today.replace(day=1)
    last_month = (month_start - timedelta(days=1)).replace(day=1)

    # This month revenue
    this_month_rev = await db.scalar(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.user_id == user.id,
            Invoice.status == "paid",
            func.date(Invoice.paid_at) >= month_start,
        )
    )

    # Last month revenue
    last_month_rev = await db.scalar(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.user_id == user.id,
            Invoice.status == "paid",
            func.date(Invoice.paid_at) >= last_month,
            func.date(Invoice.paid_at) < month_start,
        )
    )

    # Outstanding
    outstanding = await db.scalar(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.user_id == user.id,
            Invoice.status.in_(["pending", "overdue"]),
        )
    )

    # Client stats
    total_clients = await db.scalar(
        select(func.count(Client.id)).where(Client.user_id == user.id)
    )

    active_projects = await db.scalar(
        select(func.count(Project.id)).where(
            Project.user_id == user.id,
            Project.status.in_(["in_progress", "review"]),
        )
    )

    # Proposal stats
    total_proposals = await db.scalar(
        select(func.count(Proposal.id)).where(Proposal.user_id == user.id)
    )
    accepted_proposals = await db.scalar(
        select(func.count(Proposal.id)).where(
            Proposal.user_id == user.id, Proposal.status == "accepted"
        )
    )
    proposal_rate = (accepted_proposals / total_proposals * 100) if total_proposals > 0 else 0

    # Lead stats
    active_leads = await db.scalar(
        select(func.count(Lead.id)).where(
            Lead.user_id == user.id,
            Lead.stage.notin_(["won", "lost"]),
        )
    )
    won_leads = await db.scalar(
        select(func.count(Lead.id)).where(
            Lead.user_id == user.id, Lead.stage == "won"
        )
    )

    # Time tracking
    total_hours = await db.scalar(
        select(func.coalesce(func.sum(TimeEntry.hours), 0)).where(
            TimeEntry.user_id == user.id
        )
    )
    billable_hours = await db.scalar(
        select(func.coalesce(func.sum(TimeEntry.hours), 0)).where(
            TimeEntry.user_id == user.id, TimeEntry.billable == True
        )
    )
    utilization = (float(billable_hours or 0) / float(total_hours or 1)) * 100

    # Revenue trend (last 6 months)
    trend = []
    for i in range(5, -1, -1):
        target_date = today - timedelta(days=30 * i)
        ms = target_date.replace(day=1)
        me = (ms + timedelta(days=32)).replace(day=1)
        rev = await db.scalar(
            select(func.coalesce(func.sum(Invoice.amount), 0)).where(
                Invoice.user_id == user.id,
                Invoice.status == "paid",
                func.date(Invoice.paid_at) >= ms,
                func.date(Invoice.paid_at) < me,
            )
        )
        trend.append({
            "month": ms.strftime("%b"),
            "revenue": float(rev or 0),
        })

    return {
        "revenue": {
            "this_month": float(this_month_rev or 0),
            "last_month": float(last_month_rev or 0),
            "outstanding": float(outstanding or 0),
            "growth_rate": round(
                ((float(this_month_rev or 0) - float(last_month_rev or 0)) / max(float(last_month_rev or 1), 1)) * 100, 1
            ),
        },
        "clients": {
            "total": total_clients or 0,
            "active_leads": active_leads or 0,
            "won_leads": won_leads or 0,
        },
        "projects": {
            "active": active_projects or 0,
        },
        "proposals": {
            "total": total_proposals or 0,
            "acceptance_rate": round(proposal_rate, 1),
        },
        "time": {
            "total_hours": round(float(total_hours or 0), 1),
            "billable_hours": round(float(billable_hours or 0), 1),
            "utilization": round(utilization, 1),
        },
        "revenue_trend": trend,
    }


@router.get("/forecast")
async def revenue_forecast_endpoint(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get revenue forecast for the next 6 months."""
    return await forecast_revenue(db, user.id, months_ahead=6)


@router.get("/insights")
async def business_insights(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """AI-powered business insights and recommendations."""
    from datetime import date, timedelta

    today = date.today()
    insights = []

    # Check outstanding invoices
    outstanding = await db.scalar(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.user_id == user.id,
            Invoice.status.in_(["pending", "overdue"]),
        )
    )
    if outstanding and outstanding > 0:
        insights.append({
            "type": "financial",
            "priority": "high",
            "title": f"${outstanding:,.0f} in outstanding invoices",
            "description": "Consider sending payment reminders to improve cash flow.",
            "action": "View Invoices",
            "action_url": "/invoices",
        })

    # Low utilization
    total_hours = await db.scalar(
        select(func.coalesce(func.sum(TimeEntry.hours), 0)).where(
            TimeEntry.user_id == user.id
        )
    )
    billable_hours = await db.scalar(
        select(func.coalesce(func.sum(TimeEntry.hours), 0)).where(
            TimeEntry.user_id == user.id, TimeEntry.billable == True
        )
    )
    if total_hours and total_hours > 0:
        util = float(billable_hours or 0) / float(total_hours) * 100
        if util < 60:
            insights.append({
                "type": "efficiency",
                "priority": "medium",
                "title": f"Low billable utilization: {util:.0f}%",
                "description": "Consider increasing billable rates or reducing non-billable time.",
                "action": "View Time",
                "action_url": "/time",
            })

    # Stale proposals
    from datetime import datetime, timezone
    stale = await db.execute(
        select(func.count(Proposal.id)).where(
            Proposal.user_id == user.id,
            Proposal.status == "sent",
            Proposal.sent_at < datetime.now(timezone.utc) - timedelta(days=7),
        )
    )
    stale_count = stale.scalar() or 0
    if stale_count > 0:
        insights.append({
            "type": "sales",
            "priority": "high",
            "title": f"{stale_count} proposal(s) need follow-up",
            "description": "Proposals older than 7 days have declining acceptance rates.",
            "action": "View Proposals",
            "action_url": "/proposals",
        })

    # Growth opportunity
    avg_project = await db.scalar(
        select(func.avg(Project.amount)).where(
            Project.user_id == user.id, Project.amount > 0
        )
    )
    if avg_project and avg_project > 0:
        insights.append({
            "type": "growth",
            "priority": "low",
            "title": f"Average project value: ${avg_project:,.0f}",
            "description": "Focus on upselling existing clients to increase average deal size.",
            "action": "View Clients",
            "action_url": "/clients",
        })

    return {"insights": insights}
