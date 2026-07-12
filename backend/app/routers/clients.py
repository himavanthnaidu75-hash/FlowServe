from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientOut, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientOut])
async def list_clients(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    q: str | None = Query(None, description="Search by name/email"),
):
    stmt = select(Client).where(Client.user_id == user.id)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            (Client.name.ilike(like)) | (Client.email.ilike(like))
        )
    stmt = stmt.order_by(Client.created_at.desc())
    result = await db.execute(stmt)
    clients = result.scalars().all()

    return [ClientOut.model_validate(c) for c in clients]


@router.post("", response_model=ClientOut, status_code=201)
async def create_client(
    payload: ClientCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = Client(
        user_id=user.id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        notes=payload.notes,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return ClientOut.model_validate(client)


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = await db.scalar(
        select(Client).where(Client.id == client_id, Client.user_id == user.id)
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientOut.model_validate(client)


@router.patch("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: str,
    payload: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = await db.scalar(
        select(Client).where(Client.id == client_id, Client.user_id == user.id)
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(client, key, value)

    await db.commit()
    await db.refresh(client)
    return ClientOut.model_validate(client)


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = await db.scalar(
        select(Client).where(Client.id == client_id, Client.user_id == user.id)
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    await db.delete(client)
    await db.commit()
    return None
