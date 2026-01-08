from sqlalchemy import String, DateTime, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from app.db.session import Base
from app.enums.trade_enums import TradeSide, TradeStatus, TradeResult


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    symbol: Mapped[str] = mapped_column(String(30), index=True)
    timeframe: Mapped[str] = mapped_column(String(10), index=True)

    side: Mapped[str] = mapped_column(String(10))  # TradeSide value
    status: Mapped[str] = mapped_column(String(10), index=True, default=TradeStatus.open.value)

    entry_price: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    take_profit: Mapped[float] = mapped_column(Float)

    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    close_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    result: Mapped[str] = mapped_column(String(10), default=TradeResult.unknown.value)  # win/loss

    fee_rate: Mapped[float] = mapped_column(Float, default=0.0)
    fee_paid: Mapped[float] = mapped_column(Float, default=0.0)

    pnl_abs: Mapped[float] = mapped_column(Float, default=0.0)
    pnl_pct: Mapped[float] = mapped_column(Float, default=0.0)

    strategy_name: Mapped[str] = mapped_column(String(80), default="multi_confirm_v1")
    confirmations_json: Mapped[str] = mapped_column(Text, default="{}")  # JSON string
    ai_note: Mapped[str | None] = mapped_column(Text, nullable=True)