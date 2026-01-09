"""
Simple Signal Router - Análisis técnico de un único timeframe
"""

from fastapi import APIRouter, HTTPException
from app.controllers.simple_signal_controller import SimpleSignalController
from app.services.telegram_service import TelegramService
from datetime import datetime

router = APIRouter(prefix="/trades", tags=["simple-signal"])
controller = SimpleSignalController()
telegram_service = TelegramService()


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


@router.post("/test-alert", summary="Enviar alerta de prueba a Telegram")
async def test_alert():
    """
    Envía una alerta de prueba simulando una señal LONG real.
    
    Sirve para verificar que Telegram está configurado correctamente.
    """
    try:
        # Simular una señal LONG
        test_entry = 91500.00
        test_sl = 91200.00
        test_tp = 92200.00
        
        await telegram_service.send_multi_timeframe_alert(
            symbol="BTCUSDT",
            consensus_signal="LONG",
            confidence=75.5,
            long_votes=3,
            short_votes=0,
            neutral_votes=1,
            weighted_score=2.75,
            price=91500.00,
            entry=test_entry,
            stop_loss=test_sl,
            take_profit=test_tp
        )
        
        return {
            "status": "success",
            "message": "✅ Alerta de prueba enviada a Telegram",
            "timestamp": datetime.now().isoformat(),
            "signal": "LONG",
            "entry": test_entry,
            "stop_loss": test_sl,
            "take_profit": test_tp,
            "expected_message": "Deberías recibir un mensaje en Telegram en segundos..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando alerta: {str(e)}")
