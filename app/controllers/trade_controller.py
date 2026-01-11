from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.trade_schema import CreateTradeRequest
from app.services.trade_manager import TradeRepository
from app.services.market_service import MarketService
from app.services.trade_manager import StrategyEngine
from app.services.chart_service import ChartService
from app.controllers import ai_controller
from app.config.settings import settings

repo = TradeRepository()
market = MarketService()
charts = ChartService()


async def get_live_signal(session: AsyncSession):
    df = await market.get_klines_df(symbol=settings.SYMBOL, timeframe=settings.TIMEFRAME)
    now_price = float(df["close"].iloc[-1])

    # Crear instancia de StrategyEngine con verbose=True para mostrar logs
    strategy = StrategyEngine(df, timeframe=settings.TIMEFRAME, verbose=True)
    signal = strategy.compute_signal()
    # signal: dict con {signal, entry, sl, tp, confirmations}
    
    # Convertir SignalType enum a string si existe
    if signal.get("signal"):
        signal["signal"] = signal["signal"].value
    
    # Preparar contexto de mercado para IA
    market_context = {
        "current_price": now_price,
        "recent_high": float(df["high"].tail(20).max()),
        "recent_low": float(df["low"].tail(20).min()),
        "volume_avg": float(df["volume"].tail(20).mean()),
    }
    
    if settings.AI_ENABLED:
        # Usar nueva arquitectura de Bedrock para validar signal
        ai_validation = await ai_controller.validate_signal_quality(
            signal=signal,
            symbol=settings.SYMBOL,
            timeframe=settings.TIMEFRAME,
            market_context=market_context
        )
        # Extraer información de validación
        signal["ai_note"] = ai_validation.get("reasoning", "No disponible")
        signal["ai_quality_score"] = ai_validation.get("quality_score", 0)
        signal["ai_recommendation"] = ai_validation.get("recommendation", "UNKNOWN")

    return {
        "symbol": settings.SYMBOL,
        "timeframe": settings.TIMEFRAME,
        "now_price": now_price,
        **signal
    }


async def create_trade(payload: dict, session: AsyncSession):
    req = CreateTradeRequest(**payload)
    trade = await repo.create_trade(
        session=session,
        symbol=settings.SYMBOL,
        timeframe=settings.TIMEFRAME,
        side=req.side.value,
        entry=req.entry_price,
        sl=req.stop_loss,
        tp=req.take_profit,
        strategy_name=req.strategy_name,
        confirmations=req.confirmations,
        ai_note=req.confirmations.get("ai_note"),
    )
    return trade


async def list_trades(session: AsyncSession, status: str | None = None):
    return await repo.list_trades(session=session, status=status)


async def get_chart(session: AsyncSession, trade_id: int):
    trade = await repo.get_trade(session=session, trade_id=trade_id)
    df = await market.get_klines_df(symbol=trade["symbol"], timeframe=trade["timeframe"])
    html = charts.render_trade_chart_html(df=df, trade=trade)
    return {"html": html}
