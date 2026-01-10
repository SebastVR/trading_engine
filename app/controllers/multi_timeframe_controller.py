"""
Multi-Timeframe Trade Controller
Maneja análisis de múltiples timeframes
"""

from typing import Dict, Any, Optional, List

from app.services.multi_timeframe_service import MultiTimeframeService, MultiTimeframeAnalysis
from app.services.chart_service import ChartService
from app.services.telegram_service import TelegramService
from app.enums.trade_enums import SignalType


class MultiTimeframeController:
    """
    Controlador para análisis multi-timeframe
    """
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.multi_tf_service = MultiTimeframeService(symbol)
        self.chart_service = ChartService()
        self.telegram_service = TelegramService()
    
    async def get_multi_timeframe_signal(self) -> Dict[str, Any]:
        """
        Obtiene señal basada en análisis multi-timeframe
        """
        try:
            # Analizar todos los timeframes
            analysis: MultiTimeframeAnalysis = await self.multi_tf_service.analyze_all_timeframes()
            
            # Formatear respuesta
            response = {
                "symbol": self.symbol,
                "consensus": {
                    "signal": analysis.consensus_signal.value if analysis.consensus_signal else None,
                    "confidence": round(analysis.confidence_score, 2),
                    "weighted_score": round(analysis.weighted_score, 2),
                    "recommendation": analysis.recommendation
                },
                "votes": {
                    "long": analysis.long_votes,
                    "short": analysis.short_votes,
                    "neutral": analysis.neutral_votes,
                    "total": len(analysis.timeframe_signals)
                },
                "timeframes": []
            }
            
            # Agregar detalles de cada timeframe
            for ts in analysis.timeframe_signals:
                tf_data = {
                    "timeframe": ts.timeframe,
                    "signal": ts.signal.value if ts.signal else None,
                    "price": round(ts.price, 2),
                    "confidence": round(ts.confidence, 2),
                    "weight": ts.weight,
                    "entry_price": ts.details.get("entry_price"),
                    "stop_loss": ts.details.get("stop_loss"),
                    "take_profit": ts.details.get("take_profit")
                }
                response["timeframes"].append(tf_data)
            
            # Si hay consenso, agregar info de trading
            if analysis.consensus_signal:
                # Buscar el timeframe con mayor peso que coincida con el consenso
                matching_signals = [
                    ts for ts in analysis.timeframe_signals 
                    if ts.signal == analysis.consensus_signal
                ]
                
                if matching_signals:
                    # Ordenar por peso (mayor primero)
                    best_signal = max(matching_signals, key=lambda x: x.weight)
                    
                    response["trading_setup"] = {
                        "entry_price": best_signal.details.get("entry_price"),
                        "stop_loss": best_signal.details.get("stop_loss"),
                        "take_profit": best_signal.details.get("take_profit"),
                        "based_on_timeframe": best_signal.timeframe,
                        "risk_reward_ratio": self._calculate_rr_ratio(
                            best_signal.details.get("entry_price"),
                            best_signal.details.get("stop_loss"),
                            best_signal.details.get("take_profit")
                        )
                    }
                    
                    # 📱 Enviar alerta a Telegram si hay consenso con buena confianza (reducido de 50% a 40%)
                    if analysis.confidence_score >= 40:
                        await self.telegram_service.send_multi_timeframe_alert(
                            symbol=self.symbol,
                            consensus_signal=analysis.consensus_signal.value,
                            confidence=analysis.confidence_score,
                            long_votes=analysis.long_votes,
                            short_votes=analysis.short_votes,
                            neutral_votes=analysis.neutral_votes,
                            weighted_score=analysis.weighted_score,
                            price=best_signal.price,
                            entry=best_signal.details.get("entry_price"),
                            stop_loss=best_signal.details.get("stop_loss"),
                            take_profit=best_signal.details.get("take_profit")
                        )
                        
                        # 💾 Guardar automáticamente en BD cuando se envía a Telegram
                        try:
                            import json
                            from app.services.trade_manager import TradeRepository
                            from app.db.session import AsyncSessionLocal
                            
                            # Convertir reason (dict) a JSON string para ai_note
                            ai_note_str = f"Consenso Multi-TF: {analysis.long_votes}L/{analysis.short_votes}S/{analysis.neutral_votes}N"
                            
                            # Crear trade en un nuevo event loop (Celery context)
                            async def save_to_db():
                                async with AsyncSessionLocal() as session:
                                    repo = TradeRepository()
                                    return await repo.create_trade(
                                        session=session,
                                        symbol=self.symbol,
                                        timeframe="multi",
                                        side=analysis.consensus_signal.value.lower(),
                                        entry=best_signal.details.get("entry_price"),
                                        sl=best_signal.details.get("stop_loss"),
                                        tp=best_signal.details.get("take_profit"),
                                        strategy_name="multi_timeframe_consensus",
                                        confirmations={
                                            "long_votes": analysis.long_votes,
                                            "short_votes": analysis.short_votes,
                                            "neutral_votes": analysis.neutral_votes,
                                            "confidence": analysis.confidence_score,
                                            "weighted_score": analysis.weighted_score,
                                        },
                                        ai_note=ai_note_str
                                    )
                            
                            # Ejecutar en un thread pool para evitar conflicto de event loops
                            import concurrent.futures
                            import asyncio
                            
                            try:
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
                            
                            print(f"✅ Trade guardado en BD: {self.symbol} {analysis.consensus_signal.value}")
                        except Exception as e:
                            import traceback
                            print(f"⚠️  Error guardando trade en BD: {e}")
                            traceback.print_exc()
            
            return response
            
        except Exception as e:
            print(f"❌ Error en multi-timeframe controller: {e}")
            raise
    
    def _calculate_rr_ratio(
        self, 
        entry: Optional[float], 
        stop_loss: Optional[float], 
        take_profit: Optional[float]
    ) -> Optional[float]:
        """
        Calcula el ratio riesgo/beneficio
        """
        if not all([entry, stop_loss, take_profit]):
            return None
        
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk > 0:
            return round(reward / risk, 2)
        
        return None
