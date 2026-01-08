"""
Test Telegram Router
Endpoint para probar alertas de Telegram
"""

from fastapi import APIRouter

from app.services.telegram_service import TelegramService

router = APIRouter(prefix="/test", tags=["Testing"])


@router.get("/telegram")
async def test_telegram():
    """
    Envía un mensaje de prueba a Telegram para verificar la configuración
    """
    telegram = TelegramService()
    
    if not telegram.enabled:
        return {
            "success": False,
            "message": "Telegram no está configurado. Verifica TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env"
        }
    
    # Enviar mensaje de prueba
    success = await telegram.send_message(
        "<b>🧪 Prueba de Telegram</b>\n\n"
        "✅ El bot está correctamente configurado y puede enviar alertas.\n\n"
        f"Bot Token: ...{telegram.bot_token[-10:]}\n"
        f"Chat ID: {telegram.chat_id}"
    )
    
    return {
        "success": success,
        "message": "Mensaje enviado correctamente" if success else "Error al enviar mensaje",
        "telegram_enabled": telegram.enabled,
        "bot_token_configured": bool(telegram.bot_token),
        "chat_id_configured": bool(telegram.chat_id)
    }


@router.post("/telegram/signal")
async def test_telegram_signal():
    """
    Envía una alerta de señal simulada para probar el formato
    """
    telegram = TelegramService()
    
    if not telegram.enabled:
        return {
            "success": False,
            "message": "Telegram no está configurado"
        }
    
    # Simular señal LONG
    success = await telegram.send_signal_alert(
        symbol="BTCUSDT",
        signal_type="LONG",
        confidence=75.5,
        price=91000.00,
        entry=91000.00,
        stop_loss=89500.00,
        take_profit=94000.00,
        timeframe="4h"
    )
    
    return {
        "success": success,
        "message": "Alerta de señal enviada" if success else "Error al enviar alerta"
    }


@router.post("/telegram/consensus")
async def test_telegram_consensus():
    """
    Envía una alerta de consenso multi-timeframe simulada
    """
    telegram = TelegramService()
    
    if not telegram.enabled:
        return {
            "success": False,
            "message": "Telegram no está configurado"
        }
    
    # Simular consenso
    success = await telegram.send_multi_timeframe_alert(
        symbol="BTCUSDT",
        consensus_signal="LONG",
        confidence=80.0,
        long_votes=3,
        short_votes=0,
        neutral_votes=1,
        weighted_score=45.5,
        price=91000.00,
        entry=91000.00,
        stop_loss=89500.00,
        take_profit=94000.00
    )
    
    return {
        "success": success,
        "message": "Alerta de consenso enviada" if success else "Error al enviar alerta"
    }
