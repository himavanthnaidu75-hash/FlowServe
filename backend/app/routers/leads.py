from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.lead import Lead
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate
from app.services.lead_scorer import score_lead, calculate_user_history, suggest_lead_stage

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadOut])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    stage: str | None = None,
    source: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    stmt = select(Lead).where(Lead.user_id == user.id)
    if stage:
        stmt = stmt.where(Lead.stage == stage)
    if source:
        stmt = stmt.where(Lead.source == source)
    stmt = stmt.order_by(Lead.score.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [LeadOut.model_validate(l) for l in result.scalars().all()]


@router.post("", response_model=LeadOut, status_code=201)
async def create_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = Lead(
        user_id=user.id,
        name=payload.name,
        email=payload.email,
        company=payload.company,
        phone=payload.phone,
        website=payload.website,
        description=payload.description,
        source=payload.source,
        estimated_budget=payload.estimated_budget,
        currency=payload.currency,
        project_type=payload.project_type,
        urgency=payload.urgency,
        tags=payload.tags,
        notes=payload.notes,
    )

    # Auto-score
    history = await calculate_user_history(db, user.id)
    lead.score = score_lead(lead, history)

    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = await db.scalar(select(Lead).where(Lead.id == lead_id, Lead.user_id == user.id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadOut.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = await db.scalar(select(Lead).where(Lead.id == lead_id, Lead.user_id == user.id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(lead, key, value)

    # Re-score
    history = await calculate_user_history(db, user.id)
    lead.score = score_lead(lead, history)

    await db.commit()
    await db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = await db.scalar(select(Lead).where(Lead.id == lead_id, Lead.user_id == user.id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()


@router.post("/{lead_id}/convert", response_model=LeadOut)
async def convert_lead_to_client(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Convert a won lead into a client."""
    from app.models.client import Client

    lead = await db.scalar(select(Lead).where(Lead.id == lead_id, Lead.user_id == user.id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.stage == "won":
        raise HTTPException(status_code=400, detail="Lead already converted")

    client = Client(
        user_id=user.id,
        name=lead.name,
        email=lead.email or "unknown@placeholder.com",
        phone=lead.phone,
        company=lead.company,
        notes=f"Converted from lead: {lead.id}",
    )
    db.add(client)
    await db.flush()

    lead.stage = "won"
    lead.converted_client_id = client.id
    lead.converted_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.get("/pipeline/summary")
async def pipeline_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get lead pipeline summary with counts and values per stage."""
    stages = ["new", "contacted", "qualified", "proposal_sent", "negotiating", "won", "lost"]
    summary = {}

    for stage in stages:
        result = await db.execute(
            select(
                Lead.stage,
                Lead.estimated_budget,
            ).where(Lead.user_id == user.id, Lead.stage == stage)
        )
        leads = result.all()
        summary[stage] = {
            "count": len(leads),
            "total_value": sum(float(l.estimated_budget or 0) for l in leads),
            "avg_score": sum(l.score for l in leads) // len(leads) if leads else 0,
        }

    total_pipeline = sum(
        s["total_value"] for stage, s in summary.items() if stage not in ["won", "lost"]
    )

    return {
        "stages": summary,
        "total_pipeline": round(total_pipeline, 2),
        "conversion_rate": round(
            summary["won"]["count"] / max(sum(s["count"] for s in summary.values()), 1) * 100, 1
        ),
    }


@router.get("/suggestions")
async def lead_suggestions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get AI-powered suggestions for lead management."""
    history = await calculate_user_history(db, user.id)

    # Get top leads by score
    top_leads = await db.execute(
        select(Lead)
        .where(Lead.user_id == user.id, Lead.stage.notin_(["won", "lost"]))
        .order_by(Lead.score.desc())
        .limit(5)
    )

    suggestions = []
    for lead in top_leads.scalars().all():
        suggested_stage = suggest_lead_stage(lead)
        if suggested_stage != lead.stage:
            suggestions.append({
                "lead_id": lead.id,
                "lead_name": lead.name,
                "current_stage": lead.stage,
                "suggested_stage": suggested_stage,
                "reason": f"Score {lead.score}/100 — {'High priority' if lead.score >= 70 else 'Worth pursuing'}",
            })

    # General tips
    tips = []
    if history["conversion_rate"] < 20:
        tips.append("Your conversion rate is below 20%. Consider improving follow-up timing.")
    if history["avg_project_value"] < 1000:
        tips.append("Average project value is low. Consider upselling or targeting higher-budget clients.")

    return {
        "suggestions": suggestions,
        "tips": tips,
        "history": history,
    }
