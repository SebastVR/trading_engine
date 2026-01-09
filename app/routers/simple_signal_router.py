"""
Simple Signal Router - Análisis técnico de un único timeframe
"""

from fastapi import APIRouter, HTTPException
from app.controllers.simple_signal_controller import SimpleSignalController

router = APIRouter(prefix="/trades", tags=["simple-signal"])
controller = SimpleSignalController()


@router.get("/simple-signal", summary="Obtener señal técnica simple (15m)")
async def get_simple_signal():
    """
    Análisis técnico simple sin consenso multi-timeframe.
    
    - Usa solo 15m
    - Genera más señales
    - Sin filtro de consenso
    - Experimental para comparar con multi-timeframe
    """
    try:
        result = await controller.get_simple_signal(timeframe="15m")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
