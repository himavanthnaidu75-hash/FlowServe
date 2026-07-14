"""
Revenue Forecasting — predicts future revenue based on historical data,
pipeline health, and seasonal patterns.
"""
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.lead import Lead
from app.models.time_entry import TimeEntry


async def forecast_revenue(db: AsyncSession, user_id: str, months_ahead: int = 6) -> dict:
    """Generate revenue forecast for the next N months."""
    today = date.today()

    # Historical monthly revenue (last 12 months)
    historical = await _get_historical_revenue(db, user_id, months=12)

    # Pipeline value (proposals sent + leads in negotiation)
    pipeline = await _get_pipeline_value(db, user_id)

    # Recurring revenue estimate
    recurring = await _estimate_recurring(db, user_id)

    # Seasonal factors
    seasonal = _get_seasonal_factors()

    # Generate forecast
    forecast = []
    avg_monthly = sum(historical.values()) / len(historical) if historical else 0

    for i in range(months_ahead):
        target_month = today + timedelta(days=30 * (i + 1))
        month_key = target_month.strftime("%Y-%m")
        month_name = target_month.strftime("%b %Y")

        # Base estimate from historical average
        base = avg_monthly

        # Apply seasonal factor
        month_num = target_month.month
        seasonal_factor = seasonal.get(month_num, 1.0)

        # Pipeline contribution (weighted by probability)
        pipeline_contribution = pipeline.get("weighted_value", 0) / months_ahead

        # Recurring contribution
        recurring_contribution = recurring.get("monthly_estimate", 0)

        # Confidence decreases with distance
        confidence = max(0.3, 1.0 - (i * 0.1))

        estimated = (base * seasonal_factor) + pipeline_contribution + recurring_contribution

        forecast.append({
            "month": month_name,
            "month_key": month_key,
            "estimated": round(estimated, 2),
            "low": round(estimated * 0.7, 2),
            "high": round(estimated * 1.3, 2),
            "confidence": round(confidence, 2),
            "pipeline_weight": round(pipeline_contribution, 2),
            "recurring_weight": round(recurring_contribution, 2),
        })

    return {
        "forecast": forecast,
        "historical_monthly": [{"month": k, "revenue": v} for k, v in historical.items()],
        "pipeline_summary": pipeline,
        "recurring_summary": recurring,
        "total_forecast_6m": round(sum(f["estimated"] for f in forecast), 2),
        "avg_monthly_forecast": round(sum(f["estimated"] for f in forecast) / len(forecast), 2) if forecast else 0,
    }


async def _get_historical_revenue(db: AsyncSession, user_id: str, months: int = 12) -> dict:
    """Get monthly revenue for the last N months."""
    from sqlalchemy import extract

    today = date.today()
    result = await db.execute(
        select(
            extract("year", Invoice.paid_at).label("year"),
            extract("month", Invoice.paid_at).label("month"),
            func.coalesce(func.sum(Invoice.amount), 0).label("revenue"),
        )
        .where(
            Invoice.user_id == user_id,
            Invoice.status == "paid",
            Invoice.paid_at.isnot(None),
            Invoice.paid_at >= datetime.now(timezone.utc) - timedelta(days=months * 31),
        )
        .group_by("year", "month")
        .order_by("year", "month")
    )

    monthly = {}
    for row in result.all():
        key = f"{int(row.year)}-{int(row.month):02d}"
        monthly[key] = float(row.revenue)

    return monthly


async def _get_pipeline_value(db: AsyncSession, user_id: str) -> dict:
    """Calculate pipeline value and weighted probability."""
    # Proposals sent
    proposals = await db.execute(
        select(func.coalesce(func.sum(Proposal.amount), 0)).where(
            Proposal.user_id == user_id,
            Proposal.status == "sent",
        )
    )
    proposal_value = float(proposals.scalar() or 0)

    # Leads in negotiation
    leads = await db.execute(
        select(func.coalesce(func.sum(Lead.estimated_budget), 0)).where(
            Lead.user_id == user_id,
            Lead.stage.in_(["qualified", "proposal_sent", "negotiating"]),
        )
    )
    lead_value = float(leads.scalar() or 0)

    # Win rates by stage
    stage_probabilities = {
        "qualified": 0.4,
        "proposal_sent": 0.6,
        "negotiating": 0.8,
    }

    weighted = proposal_value * 0.6 + lead_value * 0.5  # Conservative weighting

    return {
        "proposal_value": round(proposal_value, 2),
        "lead_value": round(lead_value, 2),
        "total_pipeline": round(proposal_value + lead_value, 2),
        "weighted_value": round(weighted, 2),
    }


async def _estimate_recurring(db: AsyncSession, user_id: str) -> dict:
    """Estimate recurring revenue from time entries and active projects."""
    # Average monthly billing from time entries
    result = await db.execute(
        select(func.coalesce(func.sum(TimeEntry.hours * TimeEntry.hourly_rate), 0)).where(
            TimeEntry.user_id == user_id,
            TimeEntry.billable == True,
        )
    )
    total_billed = float(result.scalar() or 0)

    # Active projects count
    active = await db.execute(
        select(func.count(Project.id)).where(
            Project.user_id == user_id,
            Project.status.in_(["in_progress", "review"]),
        )
    )
    active_count = active.scalar() or 0

    # Monthly estimate based on averages
    monthly = total_billed / 12 if total_billed > 0 else 0

    return {
        "total_billed": round(total_billed, 2),
        "active_projects": active_count,
        "monthly_estimate": round(monthly, 2),
    }


def _get_seasonal_factors() -> dict:
    """Seasonal revenue multipliers (freelancing patterns)."""
    return {
        1: 0.8,   # January — post-holiday slowdown
        2: 0.85,  # February — slow
        3: 1.0,   # March — Q1 close
        4: 1.05,  # April — spring uptick
        5: 1.1,   # May — busy
        6: 1.0,   # June — mid-year
        7: 0.9,   # July — summer slowdown
        8: 0.85,  # August — vacation season
        9: 1.1,   # September — back to business
        10: 1.15, # October — Q4 push
        11: 1.1,  # November — year-end projects
        12: 0.7,  # December — holiday slowdown
    }
