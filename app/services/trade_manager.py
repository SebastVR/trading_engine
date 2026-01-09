import asyncio
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.session import AsyncSessionLocal
from app.enums.trade_enums import TradeStatus, TradeResult, SignalType
from app.models.trade_model import Trade
from app.services.market_service import MarketService
from app.services.alert_service import AlertService
from app.util.math import rsi, atr, sma


class StrategyEngine:
    """
    Confirmaciones inspiradas en lo "clásico" de libros serios:
    - Tendencia: MA rápida vs MA lenta + pendiente
    - Estructura: HH/HL para long, LH/LL para short (simplificado)
    - Acción del precio: ruptura + cierre favorable (simplificado)
    - RSI para evitar entrar "muerto" o sobre-extendido
    - ATR para SL "respirable"
    - Niveles (zona) aproximados: swing reciente tipo fib/estructura
    """

    def __init__(self, df: pd.DataFrame, timeframe: str = None, verbose: bool = True):
        self.df = df
        self.timeframe = timeframe or settings.TIMEFRAME
        self.verbose = verbose

    def compute_signal(self) -> dict:
        df = self.df
        close = df["close"].values
        high = df["high"].values
        low = df["low"].values

        ma_fast = sma(close, settings.MA_FAST)
        ma_slow = sma(close, settings.MA_SLOW)
        rsi_v = rsi(close, settings.RSI_PERIOD)
        atr_v = atr(high, low, close, period=14)

        last_price = float(close[-1])
        last_atr = float(atr_v[-1]) if not np.isnan(atr_v[-1]) else 0.0

        trend_up = ma_fast[-1] > ma_slow[-1]
        trend_down = ma_fast[-1] < ma_slow[-1]

        # estructura simple con últimos swings (muy básico)
        recent = df.tail(60).copy()
        swing_high = float(recent["high"].max())
        swing_low = float(recent["low"].min())

        # ruptura simple (cierre por encima del máximo reciente de N velas)
        lookback = 15  # Reducido de 20 a 15 para ser más sensible a breakouts
        prev_high = float(df["high"].tail(lookback).max())
        prev_low = float(df["low"].tail(lookback).min())

        breakout_up = last_price > prev_high
        breakout_down = last_price < prev_low

        # filtros RSI
        last_rsi = float(rsi_v[-1]) if not np.isnan(rsi_v[-1]) else 50.0
        rsi_ok_long = settings.RSI_MIN <= last_rsi <= settings.RSI_MAX
        rsi_ok_short = (100 - settings.RSI_MAX) <= last_rsi <= (100 - settings.RSI_MIN)

        # 📊 LOGS DE ANÁLISIS (solo si verbose=True)
        if self.verbose:
            print("\n" + "="*80)
            print(f"📊 ANÁLISIS DE MERCADO - {settings.SYMBOL} ({self.timeframe})")
            print("="*80)
            print(f"💰 Precio actual: ${last_price:,.2f}")
            print(f"\n🔍 CONFIRMACIONES:")
            
            # Tendencia
            print(f"\n1️⃣  TENDENCIA (MA {settings.MA_FAST} vs MA {settings.MA_SLOW}):")
            print(f"   MA Fast: {ma_fast[-1]:.2f}")
            print(f"   MA Slow: {ma_slow[-1]:.2f}")
            if trend_up:
                print(f"   ✅ Tendencia ALCISTA (MA Fast > MA Slow)")
            elif trend_down:
                print(f"   ✅ Tendencia BAJISTA (MA Fast < MA Slow)")
            else:
                print(f"   ⚠️  Sin tendencia clara")
            
            # Estructura / Breakout
            print(f"\n2️⃣  RUPTURA (Breakout últimas {lookback} velas):")
            print(f"   High previo: ${prev_high:,.2f}")
            print(f"   Low previo: ${prev_low:,.2f}")
            print(f"   Precio actual: ${last_price:,.2f}")
            if breakout_up:
                print(f"   ✅ BREAKOUT ALCISTA (precio > high previo)")
            elif breakout_down:
                print(f"   ✅ BREAKOUT BAJISTA (precio < low previo)")
            else:
                diff_to_high = ((prev_high - last_price) / last_price) * 100
                diff_to_low = ((last_price - prev_low) / last_price) * 100
                print(f"   ❌ Sin breakout (falta {diff_to_high:.2f}% para high, {diff_to_low:.2f}% desde low)")
            
            # RSI
            print(f"\n3️⃣  RSI (periodo {settings.RSI_PERIOD}):")
            print(f"   RSI actual: {last_rsi:.2f}")
            print(f"   Rango LONG: {settings.RSI_MIN} - {settings.RSI_MAX}")
            print(f"   Rango SHORT: {100 - settings.RSI_MAX} - {100 - settings.RSI_MIN}")
            if rsi_ok_long:
                print(f"   ✅ RSI OK para LONG ({last_rsi:.1f} en rango)")
            elif rsi_ok_short:
                print(f"   ✅ RSI OK para SHORT ({last_rsi:.1f} en rango)")
            elif last_rsi < settings.RSI_MIN:
                print(f"   ⚠️  RSI bajo ({last_rsi:.1f} < {settings.RSI_MIN}) - Sobreventa")
            elif last_rsi > settings.RSI_MAX and last_rsi < (100 - settings.RSI_MAX):
                print(f"   ⚠️  RSI en zona neutral")
            else:
                print(f"   ⚠️  RSI alto ({last_rsi:.1f}) - Sobrecompra")
            
            # ATR
            print(f"\n4️⃣  ATR (volatilidad):")
            print(f"   ATR actual: ${last_atr:.2f}")
            if last_atr > 0:
                print(f"   ✅ ATR válido para calcular SL")
            else:
                print(f"   ❌ ATR inválido")
            
            # Estructura de swings
            print(f"\n5️⃣  ESTRUCTURA (últimos 60 velas):")
            print(f"   Swing High: ${swing_high:,.2f}")
            print(f"   Swing Low: ${swing_low:,.2f}")
            print(f"   Rango: ${swing_high - swing_low:,.2f}")

            # Resumen de señal LONG
            print(f"\n📈 EVALUACIÓN LONG:")
            print(f"   {'✅' if trend_up else '❌'} Tendencia alcista")
            print(f"   {'✅' if breakout_up else '❌'} Breakout alcista")
            print(f"   {'✅' if rsi_ok_long else '❌'} RSI en rango LONG")
            print(f"   {'✅' if last_atr > 0 else '❌'} ATR válido")
            long_valid = trend_up and breakout_up and rsi_ok_long and last_atr > 0
            print(f"   {'🟢 SEÑAL LONG VÁLIDA' if long_valid else '🔴 No cumple todos los requisitos'}")

            # Resumen de señal SHORT
            print(f"\n📉 EVALUACIÓN SHORT:")
            print(f"   {'✅' if trend_down else '❌'} Tendencia bajista")
            print(f"   {'✅' if breakout_down else '❌'} Breakout bajista")
            print(f"   {'✅' if rsi_ok_short else '❌'} RSI en rango SHORT")
            print(f"   {'✅' if last_atr > 0 else '❌'} ATR válido")
            short_valid = trend_down and breakout_down and rsi_ok_short and last_atr > 0
            print(f"   {'🟢 SEÑAL SHORT VÁLIDA' if short_valid else '🔴 No cumple todos los requisitos'}")
            print("="*80 + "\n")

        # señal long
        if trend_up and breakout_up and rsi_ok_long and last_atr > 0:
            entry = last_price
            sl = entry - settings.ATR_MULTIPLIER_SL * last_atr
            tp = entry + settings.RISK_REWARD * (entry - sl)

            if self.verbose:
                print("🎯 GENERANDO SEÑAL LONG")
                print(f"   Entry: ${entry:,.2f}")
                print(f"   Stop Loss: ${sl:,.2f} (riesgo: ${entry - sl:,.2f})")
                print(f"   Take Profit: ${tp:,.2f} (reward: ${tp - entry:,.2f})")
                print(f"   R:R = {settings.RISK_REWARD}:1\n")

            return {
                "signal": SignalType.LONG,
                "reason": {
                    "trend": "up (MA fast > MA slow)",
                    "breakout": f"close > high({lookback})",
                    "structure_zone": {"swing_low": swing_low, "swing_high": swing_high},
                    "rsi": last_rsi,
                    "atr": last_atr,
                },
                "entry": entry,
                "stop_loss": sl,
                "take_profit": tp,
            }

        # señal short
        if trend_down and breakout_down and rsi_ok_short and last_atr > 0:
            entry = last_price
            sl = entry + settings.ATR_MULTIPLIER_SL * last_atr
            tp = entry - settings.RISK_REWARD * (sl - entry)

            if self.verbose:
                print("🎯 GENERANDO SEÑAL SHORT")
                print(f"   Entry: ${entry:,.2f}")
                print(f"   Stop Loss: ${sl:,.2f} (riesgo: ${sl - entry:,.2f})")
                print(f"   Take Profit: ${tp:,.2f} (reward: ${entry - tp:,.2f})")
                print(f"   R:R = {settings.RISK_REWARD}:1\n")

            return {
                "signal": SignalType.SHORT,
                "reason": {
                    "trend": "down (MA fast < MA slow)",
                    "breakout": f"close < low({lookback})",
                    "structure_zone": {"swing_low": swing_low, "swing_high": swing_high},
                    "rsi": last_rsi,
                    "atr": last_atr,
                },
                "entry": entry,
                "stop_loss": sl,
                "take_profit": tp,
            }

        return {"signal": None, "reason": {"note": "No setup con confirmaciones suficientes"}}


class TradeRepository:
    async def create_trade(
        self,
        session: AsyncSession,
        symbol: str,
        timeframe: str,
        side: str,
        entry: float,
        sl: float,
        tp: float,
        strategy_name: str,
        confirmations: dict,
        ai_note: str | None = None,
    ) -> dict:
        confirmations_json = json.dumps(confirmations, ensure_ascii=False)
        fee_rate = settings.BINANCE_TAKER_FEE  # simplificado

        trade = Trade(
            symbol=symbol,
            timeframe=timeframe,
            side=side,
            status=TradeStatus.open.value,
            entry_price=entry,
            stop_loss=sl,
            take_profit=tp,
            fee_rate=fee_rate,
            confirmations_json=confirmations_json,
            ai_note=ai_note,
            strategy_name=strategy_name,
        )
        session.add(trade)
        await session.commit()
        await session.refresh(trade)
        return self._to_dict(trade)

    async def list_trades(self, session: AsyncSession, status: str | None = None) -> dict:
        q = select(Trade).order_by(Trade.id.desc())
        if status:
            q = q.where(Trade.status == status)
        res = await session.execute(q)
        items = [self._to_dict(t) for t in res.scalars().all()]
        return {"items": items, "total": len(items)}

    async def get_trade(self, session: AsyncSession, trade_id: int) -> dict:
        res = await session.execute(select(Trade).where(Trade.id == trade_id))
        t = res.scalar_one()
        return self._to_dict(t)

    async def get_open_trades(self, session: AsyncSession) -> list[Trade]:
        res = await session.execute(select(Trade).where(Trade.status == TradeStatus.open.value))
        return list(res.scalars().all())

    async def close_trade(
        self,
        session: AsyncSession,
        trade: Trade,
        close_price: float,
        result: str,
    ) -> None:
        # PnL simple “1 unidad”
        entry = trade.entry_price
        pnl_abs = (close_price - entry) if trade.side == "long" else (entry - close_price)
        pnl_pct = (pnl_abs / entry) * 100 if entry else 0.0

        # fee aproximado: entrada + salida
        fee_paid = trade.fee_rate * (entry + close_price)

        await session.execute(
            update(Trade)
            .where(Trade.id == trade.id)
            .values(
                status=TradeStatus.closed.value,
                closed_at=datetime.now(timezone.utc),
                close_price=close_price,
                result=result,
                pnl_abs=pnl_abs - fee_paid,
                pnl_pct=pnl_pct,
                fee_paid=fee_paid,
            )
        )
        await session.commit()

    def _to_dict(self, t: Trade) -> dict:
        return {
            "id": t.id,
            "symbol": t.symbol,
            "timeframe": t.timeframe,
            "side": t.side,
            "status": t.status,
            "entry_price": t.entry_price,
            "stop_loss": t.stop_loss,
            "take_profit": t.take_profit,
            "opened_at": t.opened_at,
            "closed_at": t.closed_at,
            "close_price": t.close_price,
            "result": t.result,
            "fee_rate": t.fee_rate,
            "fee_paid": t.fee_paid,
            "pnl_abs": t.pnl_abs,
            "pnl_pct": t.pnl_pct,
            "strategy_name": t.strategy_name,
            "confirmations": json.loads(t.confirmations_json or "{}"),
            "ai_note": t.ai_note,
        }


class TradeManager:
    """
    Loop en tiempo real:
    - Descarga velas
    - Evalúa trades abiertos vs SL/TP
    - Emite alerta de cierre (win/loss)
    """

    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._running = False
        self.market = MarketService()
        self.alerts = AlertService()
        self.repo = TradeRepository()

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    async def _loop(self) -> None:
        while self._running:
            try:
                df = await self.market.get_klines_df(
                    symbol=settings.SYMBOL,
                    timeframe=settings.TIMEFRAME,
                    limit=settings.CANDLES_LIMIT,
                )
                now_price = float(df["close"].iloc[-1])

                async with AsyncSessionLocal() as session:
                    open_trades = await self.repo.get_open_trades(session)
                    for t in open_trades:
                        hit = self._check_hit(t, now_price)
                        if hit:
                            result, close_price = hit
                            await self.repo.close_trade(session, t, close_price=close_price, result=result)
                            await self.alerts.send_close_alert({
                                "trade_id": t.id,
                                "symbol": t.symbol,
                                "timeframe": t.timeframe,
                                "side": t.side,
                                "result": result,
                                "close_price": close_price,
                                "entry": t.entry_price,
                                "sl": t.stop_loss,
                                "tp": t.take_profit
                            })

            except Exception as e:
                print(f"[TradeManager] error: {e}")

            await asyncio.sleep(settings.POLL_SECONDS)

    def _check_hit(self, t: Trade, price: float):
        if t.side == "long":
            if price <= t.stop_loss:
                return (TradeResult.loss.value, price)
            if price >= t.take_profit:
                return (TradeResult.win.value, price)
        else:
            if price >= t.stop_loss:
                return (TradeResult.loss.value, price)
            if price <= t.take_profit:
                return (TradeResult.win.value, price)
        return None
