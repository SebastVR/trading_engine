"""
Simple Signal Controller (Análisis de un solo timeframe - 15m)
Sin consenso multi-timeframe, solo técnico puro.
"""

from typing import Dict, Any

from app.services.market_service import MarketService
from app.services.trade_manager import StrategyEngine
from app.services.telegram_service import TelegramService
from app.config.settings import settings
from app.controllers import ai_controller


def _parse_allowed_hours(spec: str) -> set[int]:
    """Parse an hour spec like "7-17,19-20" into a set of hours (0-23)."""
    spec = (spec or "").strip()
    if not spec:
        return set()

    hours: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            start = int(a.strip())
            end = int(b.strip())
            for h in range(min(start, end), max(start, end) + 1):
                if 0 <= h <= 23:
                    hours.add(h)
        else:
            h = int(chunk)
            if 0 <= h <= 23:
                hours.add(h)
    return hours


def _now_hour_colombia() -> int:
    # No dependemos de pytz: UTC-5 fijo para Colombia.
    from datetime import datetime, timezone, timedelta

    co_tz = timezone(timedelta(hours=-5))
    return datetime.now(co_tz).hour


class SimpleSignalController:
    """
    Análisis técnico simple sin multi-timeframe
    - Solo usa 15m
    - Genera señales basadas en indicadores de ese timeframe
    - Sin consenso requerido (más señales)
    """
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.market_service = MarketService()
        self.telegram_service = TelegramService()
    
    async def get_simple_signal(self, timeframe: str = "15m") -> Dict[str, Any]:
        """
        Obtiene señal técnica simple de un único timeframe
        """
        try:
            # Obtener datos del mercado
            df = await self.market_service.get_klines_df(
                symbol=self.symbol,
                timeframe=timeframe,
                limit=300
            )
            
            if df.empty:
                return {
                    "symbol": self.symbol,
                    "timeframe": timeframe,
                    "signal": None,
                    "error": "No data available"
                }
            
            # Analizar con StrategyEngine (técnico puro)
            engine = StrategyEngine(df, timeframe=timeframe, verbose=True)
            signal_result = engine.compute_signal()

            # IA Filter (FASE 1): evaluar la señal antes de alertar/guardar
            if settings.AI_ENABLED and signal_result.get("signal"):
                market_context = {
                    "current_price": float(df["close"].iloc[-1]),
                    "recent_high": float(df["high"].tail(20).max()),
                    "recent_low": float(df["low"].tail(20).min()),
                    "volume_avg": float(df["volume"].tail(20).mean()),
                }

                # El validador espera el mismo shape que el controller principal (signal/entry/sl/tp/confirmations)
                signal_for_ai = {
                    "signal": signal_result["signal"].value if signal_result.get("signal") else None,
                    "entry": signal_result.get("entry"),
                    "stop_loss": signal_result.get("stop_loss"),
                    "take_profit": signal_result.get("take_profit"),
                    "confirmations": signal_result.get("reason"),
                }

                try:
                    ai_validation = await ai_controller.validate_signal_quality(
                        signal=signal_for_ai,
                        symbol=self.symbol,
                        timeframe=timeframe,
                        market_context=market_context,
                    )
                except Exception as e:
                    # Nunca tumbar el endpoint por un fallo de IA/parseo.
                    ai_validation = {
                        "quality_score": None,
                        "recommendation": "WAIT",
                        "reasoning": f"ai_error: {e}",
                    }

                # Adjuntar resultado IA al signal_result para downstream (Telegram/DB)
                signal_result["ai_validation"] = ai_validation
                # Normalizar shape (evitar None/strings raros)
                signal_result["ai_note"] = ai_validation.get("reasoning")
                signal_result["ai_quality_score"] = ai_validation.get("quality_score")
                signal_result["ai_recommendation"] = ai_validation.get("recommendation")
            
            # Formatear respuesta
            response = {
                "symbol": self.symbol,
                "timeframe": timeframe,
                "price": float(df["close"].iloc[-1]),
                "signal": signal_result["signal"].value if signal_result["signal"] else None,
                "entry": signal_result.get("entry"),
                "stop_loss": signal_result.get("stop_loss"),
                "take_profit": signal_result.get("take_profit"),
                "reason": signal_result.get("reason"),
                "confidence": 100.0 if signal_result["signal"] else 0.0
            }
            
            # Enviar alerta a Telegram si hay señal
            if signal_result["signal"]:
                # Incluir datos IA también en la respuesta del endpoint
                response["ai_recommendation"] = signal_result.get("ai_recommendation")
                response["ai_quality_score"] = signal_result.get("ai_quality_score")
                response["ai_note"] = signal_result.get("ai_note")

                # Normalizar la señal una sola vez para aplicar filtros sin depender del enum interno
                signal_value = (response.get("signal") or "").upper()

                # Guardrails (optimización): horario Colombia
                allowed = _parse_allowed_hours(getattr(settings, "SIGNAL_ALLOWED_HOURS_CO", ""))
                if allowed:
                    hour_co = _now_hour_colombia()
                    if hour_co not in allowed:
                        return {
                            **response,
                            "filtered": True,
                            "filtered_reason": f"hour_not_allowed_co({hour_co})",
                        }

                # Guardrails (optimización): desactivar shorts si está configurado
                if getattr(settings, "DISABLE_SHORTS", False) and signal_value == "SHORT":
                    print("[simple-signal] filtered shorts_disabled")
                    # Incluir explícitamente `filtered: true` para facilitar monitoreo en endpoint
                    return {
                        **response,
                        "filtered": True,
                        "filtered_reason": "shorts_disabled",
                    }

                # Guardrails (optimización): enforcement IA
                # Nota: este filtro NO debería depender del envío a Telegram; se aplica a la respuesta del endpoint.
                if settings.AI_ENABLED:
                    enforce = getattr(settings, "AI_FILTER_ENFORCE", False)
                    if enforce:
                        recommendation = (response.get("ai_recommendation") or "").upper()
                        score = response.get("ai_quality_score")
                        if recommendation != "OPEN" and not (
                            isinstance(score, (int, float)) and score >= settings.AI_QUALITY_THRESHOLD
                        ):
                            print(f"[simple-signal] filtered ai_block reco={recommendation} score={score}")
                            return {
                                **response,
                                "filtered": True,
                                "filtered_reason": f"ai_block(recommendation={recommendation},score={score})",
                            }

                # Formatear reason dict como string legible
                reason_dict = signal_result.get("reason", {})
                reason_str = None
                if isinstance(reason_dict, dict):
                    reason_str = f"Trend: {reason_dict.get('trend')}, Breakout: {reason_dict.get('breakout')}"
                else:
                    reason_str = str(reason_dict)

                # Si llegamos aquí, la señal pasó los filtros. Se envía Telegram + se guarda en BD.
                
                await self.telegram_service.send_signal_alert(
                    symbol=self.symbol,
                    signal_type=signal_result["signal"].value,
                    price=response["price"],
                    entry=signal_result.get("entry"),
                    stop_loss=signal_result.get("stop_loss"),
                    take_profit=signal_result.get("take_profit"),
                    timeframe=timeframe,
                    reason=reason_str,
                    confidence=response["confidence"],
                    ai_recommendation=signal_result.get("ai_recommendation"),
                    ai_quality_score=signal_result.get("ai_quality_score"),
                    ai_reasoning=(
                        signal_result.get("ai_note")
                        or (signal_result.get("ai_validation") or {}).get("reasoning")
                    ),
                )
                
                # 💾 Guardar automáticamente en BD cuando se envía a Telegram
                try:
                    import json
                    from app.services.trade_manager import TradeRepository
                    from sqlalchemy.ext.asyncio import AsyncSession
                    from app.db.session import AsyncSessionLocal
                    
                    # Convertir reason (dict) a JSON string para ai_note
                    reason_dict = signal_result.get("reason", {})
                    # NOTA: ai_note debe reservarse para el output de la IA (Bedrock).
                    # Aquí guardamos el reason del strategy dentro de confirmations_json.
                    ai_note_str = None
                    
                    # Crear trade en un nuevo event loop (Celery context)
                    async def save_to_db():
                        async with AsyncSessionLocal() as session:
                            repo = TradeRepository()
                            return await repo.create_trade(
                                session=session,
                                symbol=self.symbol,
                                timeframe=timeframe,
                                side=signal_result["signal"].value.lower(),
                                entry=signal_result.get("entry"),
                                sl=signal_result.get("stop_loss"),
                                tp=signal_result.get("take_profit"),
                                strategy_name="simple_breakout",
                                confirmations={
                                    "reason": reason_dict,
                                    "confidence": response["confidence"],
                                },
                                ai_note=(signal_result.get("ai_note") or ai_note_str),
                                ai_quality_score=signal_result.get("ai_quality_score"),
                                ai_recommendation=signal_result.get("ai_recommendation"),
                            )
                    
                    # Ejecutar en un thread pool para evitar conflicto de event loops
                    import concurrent.futures
                    
                    # Use a sync-style execution path to avoid event loop conflicts
                    try:
                        import asyncio
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Ya estamos en loop, usar future en thread
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, save_to_db())
                                future.result(timeout=5)
                        else:
                            # No hay loop, crear uno
                            loop.run_until_complete(save_to_db())
                    except RuntimeError:
                        # No hay event loop, crear uno nuevo
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            new_loop.run_until_complete(save_to_db())
                        finally:
                            new_loop.close()
                    
                    print(f"✅ Trade guardado en BD: {self.symbol} {signal_result['signal'].value} ({timeframe})")
                except Exception as e:
                    import traceback
                    print(f"⚠️  Error guardando trade en BD: {e}")
                    traceback.print_exc()
            
            return response
            
        except Exception as e:
            print(f"❌ Error en simple signal controller: {e}")
            raise
