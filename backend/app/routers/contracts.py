from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import ContractCreate, ContractOut, ContractUpdate
from app.services.contract_generator import generate_contract

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=list[ContractOut])
async def list_contracts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    stmt = select(Contract).where(Contract.user_id == user.id)
    if status:
        stmt = stmt.where(Contract.status == status)
    stmt = stmt.order_by(Contract.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [ContractOut.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=ContractOut, status_code=201)
async def create_contract(
    payload: ContractCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Generate from template
    generated = generate_contract(
        template_type=payload.contract_type,
        variables={
            **payload.variables,
            "total_amount": payload.total_value,
            "client_name": payload.variables.get("client_name", "[Client Name]"),
        },
        custom_content=payload.content if payload.content else None,
    )

    contract = Contract(
        user_id=user.id,
        client_id=payload.client_id,
        project_id=payload.project_id,
        title=payload.title,
        contract_type=payload.contract_type,
        content=generated["content"],
        variables=generated["variables"],
        total_value=payload.total_value,
        payment_terms=payload.payment_terms,
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return ContractOut.model_validate(contract)


@router.get("/{contract_id}", response_model=ContractOut)
async def get_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contract = await db.scalar(
        select(Contract).where(Contract.id == contract_id, Contract.user_id == user.id)
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ContractOut.model_validate(contract)


@router.patch("/{contract_id}", response_model=ContractOut)
async def update_contract(
    contract_id: str,
    payload: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contract = await db.scalar(
        select(Contract).where(Contract.id == contract_id, Contract.user_id == user.id)
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(contract, key, value)

    await db.commit()
    await db.refresh(contract)
    return ContractOut.model_validate(contract)


@router.delete("/{contract_id}", status_code=204)
async def delete_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contract = await db.scalar(
        select(Contract).where(Contract.id == contract_id, Contract.user_id == user.id)
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    await db.delete(contract)
    await db.commit()


@router.post("/generate")
async def generate_from_template(
    template_type: str,
    variables: dict = {},
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Preview a generated contract from template."""
    generated = generate_contract(template_type, variables)
    return generated
