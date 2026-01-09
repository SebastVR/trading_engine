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
                await self.telegram_service.send_signal_alert(
                    symbol=self.symbol,
                    signal_type=signal_result["signal"].value,
                    price=response["price"],
                    entry=signal_result.get("entry"),
                    stop_loss=signal_result.get("stop_loss"),
                    take_profit=signal_result.get("take_profit"),
                    timeframe=timeframe,
                    reason=signal_result.get("reason")
                )
            
            return response
            
        except Exception as e:
            print(f"❌ Error en simple signal controller: {e}")
            raise
