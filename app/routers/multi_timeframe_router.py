"""
Multi-Timeframe Trade Routes
"""

from fastapi import APIRouter, HTTPException

from app.controllers.multi_timeframe_controller import MultiTimeframeController

router = APIRouter(prefix="/trades", tags=["Multi-Timeframe Trading"])


@router.get("/multi-signal")
async def get_multi_timeframe_signal():
    """
    Obtiene señal de trading basada en análisis multi-timeframe
    
    Analiza 4 timeframes (15m, 1h, 4h, 1d) y determina consenso.
    Requiere al menos 2 timeframes con la misma señal para emitir recomendación.
    
    Returns:
        Dict con:
        - consensus: Señal de consenso, confianza, score ponderado
        - votes: Cantidad de votos por cada tipo de señal
        - timeframes: Detalle de cada timeframe analizado
        - trading_setup: Niveles de entrada, SL, TP (si hay consenso)
    """
    try:
        controller = MultiTimeframeController()
        result = await controller.get_multi_timeframe_signal()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
