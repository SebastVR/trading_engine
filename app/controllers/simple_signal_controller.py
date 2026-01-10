"""
Simple Signal Controller (Análisis de un solo timeframe - 15m)
Sin consenso multi-timeframe, solo técnico puro.
"""

from typing import Dict, Any

from app.services.market_service import MarketService
from app.services.trade_manager import StrategyEngine
from app.services.telegram_service import TelegramService
from app.config.settings import settings


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
                # Formatear reason dict como string legible
                reason_dict = signal_result.get("reason", {})
                reason_str = None
                if isinstance(reason_dict, dict):
                    reason_str = f"Trend: {reason_dict.get('trend')}, Breakout: {reason_dict.get('breakout')}"
                else:
                    reason_str = str(reason_dict)
                
                await self.telegram_service.send_signal_alert(
                    symbol=self.symbol,
                    signal_type=signal_result["signal"].value,
                    price=response["price"],
                    entry=signal_result.get("entry"),
                    stop_loss=signal_result.get("stop_loss"),
                    take_profit=signal_result.get("take_profit"),
                    timeframe=timeframe,
                    reason=reason_str,
                    confidence=response["confidence"]
                )
                
                # 💾 Guardar automáticamente en BD cuando se envía a Telegram
                try:
                    import json
                    from app.services.trade_manager import TradeRepository
                    from sqlalchemy.ext.asyncio import AsyncSession
                    from app.db.session import AsyncSessionLocal
                    
                    # Convertir reason (dict) a JSON string para ai_note
                    reason_dict = signal_result.get("reason", {})
                    ai_note_str = json.dumps(reason_dict) if isinstance(reason_dict, dict) else str(reason_dict)
                    
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
                                ai_note=ai_note_str
                            )
                    
                    # Ejecutar en un thread pool para evitar conflicto de event loops
                    import concurrent.futures
                    from app.db.session import engine
                    from sqlalchemy.orm import sessionmaker
                    from sqlalchemy.orm import Session
                    
                    # Usar sesión síncrona para guardar
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
