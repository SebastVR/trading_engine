from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict, List

from app.enums.trade_enums import TradeSide, TradeStatus, TradeResult


class CreateTradeRequest(BaseModel):
    side: TradeSide
    entry_price: float
    stop_loss: float
    take_profit: float
    strategy_name: str = "multi_confirm_v1"
    confirmations: Dict[str, Any] = Field(default_factory=dict)


class TradeResponse(BaseModel):
    id: int
    symbol: str
    timeframe: str
    side: TradeSide
    status: TradeStatus

    entry_price: float
    stop_loss: float
    take_profit: float

    opened_at: datetime
    closed_at: Optional[datetime] = None

    close_price: Optional[float] = None
    result: TradeResult

    fee_rate: float
    fee_paid: float

    pnl_abs: float
    pnl_pct: float

    strategy_name: str
    confirmations: Dict[str, Any]
    ai_note: Optional[str] = None


class TradeListResponse(BaseModel):
    items: List[TradeResponse]
    total: int


class SignalResponse(BaseModel):
    symbol: str
    timeframe: str
    now_price: float
    signal: Optional[str] = None  # long/short/none
    reason: Dict[str, Any]
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    ai_note: Optional[str] = None


class ChartResponse(BaseModel):
    html: str
