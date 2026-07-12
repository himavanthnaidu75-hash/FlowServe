"""Public-facing client portal. Token-based, no JWT required."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.integrations import create_payment_link
from app.database import get_db
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.portal_token import PortalToken
from app.models.project import Project
from app.schemas.client import ClientOut
from app.schemas.invoice import InvoiceOut
from app.schemas.project import ProjectOut

router = APIRouter(prefix="/portal", tags=["portal"])


def _serialize_invoice(inv: Invoice) -> dict:
    return {
        "id": inv.id,
        "number": inv.number,
        "client_id": inv.client_id,
        "project_id": inv.project_id,
        "status": inv.status,
        "amount": float(inv.amount or 0),
        "currency": inv.currency,
        "issue_date": inv.issue_date,
        "due_date": inv.due_date,
        "paid_at": inv.paid_at,
        "line_items": inv.line_items or [],
    }


@router.get("/{token}")
async def portal_view(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    pt = await db.scalar(
        select(PortalToken)
        .where(PortalToken.token == token)
        .options(selectinload(PortalToken.client))
    )
    if not pt:
        raise HTTPException(status_code=404, detail="Invalid portal token")
    if pt.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Portal access expired")

    client = pt.client
    projects = await db.scalars(
        select(Project)
        .where(Project.client_id == client.id)
        .order_by(Project.created_at.desc())
        .options(selectinload(Project.client))
    )
    invoices = await db.scalars(
        select(Invoice).where(Invoice.client_id == client.id).order_by(Invoice.created_at.desc())
    )

    return {
        "client": ClientOut.model_validate(client).model_dump(),
        "projects": [ProjectOut.model_validate(p).model_dump() for p in projects],
        "invoices": [
            InvoiceOut.model_validate(_serialize_invoice(i)).model_dump() for i in invoices
        ],
    }


@router.post("/{token}/invoices/{invoice_id}/pay")
async def portal_pay(
    token: str,
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Public pay route — for client to mark an invoice via Stripe checkout. Stubbed for now."""
    pt = await db.scalar(
        select(PortalToken).where(PortalToken.token == token)
    )
    if not pt:
        raise HTTPException(status_code=404, detail="Invalid portal token")

    inv = await db.scalar(
        select(Invoice).where(
            Invoice.id == invoice_id, Invoice.client_id == pt.client_id
        )
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if inv.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")

    pay_url = create_payment_link(inv.number, float(inv.amount or 0), inv.currency)
    return {"pay_url": pay_url, "invoice_number": inv.number}
