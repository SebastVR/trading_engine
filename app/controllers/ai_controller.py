"""
AI Controller: Endpoints y lógica de negocio para IA Filter
"""

import logging
from typing import Optional, Dict, Any

from app.services.trading_ai_agent import trading_ai_agent
from app.services.trade_manager import TradeRepository


logger = logging.getLogger(__name__)
repo = TradeRepository()


async def validate_signal_quality(
    signal: Dict[str, Any],
    symbol: str,
    timeframe: str,
    market_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Valida la calidad de una señal usando IA.

    Args:
        signal: Dict con detalles del signal
        symbol: Par (BTCUSDT)
        timeframe: Timeframe (15m, 1h, etc)
        market_context: Contexto de mercado

    Returns:
        Dict con validación y score de calidad
    """
    logger.info(f"[ENTRY] validate_signal_quality called for {symbol}")
    try:
        logger.info(
            f"🤖 [AI CONTROLLER] Iniciando validación | {symbol} | {signal.get('signal', 'UNKNOWN')}"
        )

        # Obtener win rate histórico de trades similares (si existen)
        historical_win_rate = await _get_historical_win_rate(symbol, timeframe)
        logger.info(f"📊 [AI CONTROLLER] Historical WR: {historical_win_rate}")

        # Validar signal con IA
        logger.info(f"🔄 [AI CONTROLLER] Llamando a trading_ai_agent.validate_signal...")
        validation = await trading_ai_agent.validate_signal(
            signal=signal,
            symbol=symbol,
            timeframe=timeframe,
            market_context=market_context,
            historical_win_rate=historical_win_rate,
        )
        logger.info(f"✅ [AI CONTROLLER] Validation result: {validation.get('quality_score')}/100")

        # Agregar información adicional
        quality_score = validation.get("quality_score", 0)
        should_open = await trading_ai_agent.should_open_trade(quality_score)
        color = trading_ai_agent.get_score_color(quality_score)

        validation["should_open"] = should_open
        validation["color"] = color
        validation["historical_win_rate"] = historical_win_rate

        # Log resultado
        recommendation = validation.get("recommendation", "UNKNOWN")
        logger.info(
            f"{color} IA Filter: {recommendation} | Score: {quality_score:.0f}/100 | "
            f"Confidence: {validation.get('confidence', 'unknown')}"
        )

        return validation

    except Exception as e:
        logger.error(f"❌ Error en validate_signal_quality: {str(e)}")
        return {
            "quality_score": 0,
            "confidence": "low",
            "recommendation": "SKIP",
            "should_open": False,
            "error": str(e),
        }


async def _get_historical_win_rate(symbol: str, timeframe: str) -> Optional[float]:
    """
    Obtiene el win rate histórico de trades similares.

    Args:
        symbol: Par
        timeframe: Timeframe

    Returns:
        Win rate (0-100) o None si no hay datos
    """
    try:
        # TODO: Implementar obtención de histórico desde BD
        # Por ahora, retornar None para evitar errores de session
        return None
        
        # Código futuro:
        # trades = await repo.list_trades(session=session, status="closed")
        # if not trades or "items" not in trades:
        #     return None
        # items = trades.get("items", [])
        # similar_trades = [
        #     t for t in items
        #     if t.get("symbol") == symbol and t.get("timeframe") == timeframe
        # ]
        # if not similar_trades:
        #     return None

        # Calcular win rate
        wins = sum(1 for t in similar_trades if t.get("result") == "win")
        total = len(similar_trades)

        if total == 0:
            return None

        return (wins / total) * 100

    except Exception as e:
        logger.warning(f"⚠️ No se pudo obtener histórico: {str(e)}")
        return None


async def get_ai_insights() -> Dict[str, Any]:
    """
    Obtiene insights generales del sistema de IA.

    Returns:
        Dict con estado y estadísticas de IA
    """
    try:
        return {
            "status": "operational",
            "quality_threshold": 75,
            "model": "openai.gpt-oss-120b-1:0",
            "provider": "aws_bedrock",
            "phase": "PHASE_1_FILTER",
            "description": "IA Filter valida cada signal antes de abrir trade",
        }
    except Exception as e:
        logger.error(f"❌ Error en get_ai_insights: {str(e)}")
        return {"status": "error", "error": str(e)}
