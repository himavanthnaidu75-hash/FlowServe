import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.integrations import send_email
from app.database import get_db
from app.deps import get_current_user
from app.models.client import Client
from app.models.proposal import Proposal
from app.models.user import User
from app.schemas.proposal import ProposalCreate, ProposalOut, ProposalUpdate

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.get("", response_model=list[ProposalOut])
async def list_proposals(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = None,
):
    stmt = select(Proposal).where(Proposal.user_id == user.id)
    if status:
        stmt = stmt.where(Proposal.status == status)
    stmt = stmt.order_by(Proposal.created_at.desc())
    result = await db.execute(stmt)
    return [ProposalOut.model_validate(p) for p in result.scalars().all()]


@router.post("", response_model=ProposalOut, status_code=201)
async def create_proposal(
    payload: ProposalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = await db.scalar(
        select(Client).where(Client.id == payload.client_id, Client.user_id == user.id)
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    proposal = Proposal(
        user_id=user.id,
        client_id=payload.client_id,
        title=payload.title,
        amount=payload.amount,
        date=payload.date or datetime.now(timezone.utc).date(),
        status=payload.status or "draft",
        sections=[s.model_dump() for s in payload.sections],
    )
    db.add(proposal)
    await db.commit()
    await db.refresh(proposal)
    return ProposalOut.model_validate(proposal)


@router.get("/{proposal_id}", response_model=ProposalOut)
async def get_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    proposal = await db.scalar(
        select(Proposal).where(
            Proposal.id == proposal_id, Proposal.user_id == user.id
        )
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return ProposalOut.model_validate(proposal)


@router.patch("/{proposal_id}", response_model=ProposalOut)
async def update_proposal(
    proposal_id: str,
    payload: ProposalUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    proposal = await db.scalar(
        select(Proposal).where(
            Proposal.id == proposal_id, Proposal.user_id == user.id
        )
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    data = payload.model_dump(exclude_unset=True)
    if "sections" in data and payload.sections is not None:
        data["sections"] = [s.model_dump() for s in payload.sections]

    for key, value in data.items():
        setattr(proposal, key, value)

    await db.commit()
    await db.refresh(proposal)
    return ProposalOut.model_validate(proposal)


@router.delete("/{proposal_id}", status_code=204)
async def delete_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    proposal = await db.scalar(
        select(Proposal).where(
            Proposal.id == proposal_id, Proposal.user_id == user.id
        )
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    await db.delete(proposal)
    await db.commit()


@router.post("/{proposal_id}/send", response_model=ProposalOut)
async def send_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    proposal = await db.scalar(
        select(Proposal)
        .where(Proposal.id == proposal_id, Proposal.user_id == user.id)
        .options(selectinload(Proposal.client))
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if proposal.status == "accepted":
        raise HTTPException(status_code=400, detail="Proposal already accepted")

    proposal.status = "sent"
    proposal.sent_at = datetime.now(timezone.utc)

    html = f"""
    <h2>{proposal.title}</h2>
    <p>Hi {proposal.client.name},</p>
    <p>You have a new proposal waiting for your review. Please log in to your client portal
    to view and approve it.</p>
    <ul>
      <li>Amount: ${proposal.amount}</li>
    </ul>
    <p>— {user.name}</p>
    """
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, send_email, proposal.client.email, f"New proposal: {proposal.title}", html)

    await db.commit()
    await db.refresh(proposal)
    return ProposalOut.model_validate(proposal)
