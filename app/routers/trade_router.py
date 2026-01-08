from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.controllers.trade_controller import (
    create_trade,
    list_trades,
    get_live_signal,
    get_chart,
)

router = APIRouter()

@router.get("/signal")
async def live_signal(
    session: AsyncSession = Depends(get_session),
):
    return await get_live_signal(session)

@router.post("")
async def open_trade(
    payload: dict,
    session: AsyncSession = Depends(get_session),
):
    return await create_trade(payload, session)

@router.get("")
async def trades(
    status: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    return await list_trades(session, status=status)

@router.get("/{trade_id}/chart")
async def trade_chart(
    trade_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await get_chart(session, trade_id=trade_id)
