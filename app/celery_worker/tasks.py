"""
Celery Tasks - Monitoreo automático del mercado
"""
import asyncio
from datetime import datetime
from typing import Optional

from app.celery_worker.celery_app import celery_app
from app.controllers.multi_timeframe_controller import MultiTimeframeController
from app.config.settings import get_settings

# Variable para rastrear la última señal enviada (evitar spam)
_last_signal_sent = {
    "signal": None,
    "timestamp": None,
    "price": None
}


@celery_app.task(name="app.celery_worker.tasks.monitor_market_signals")
def monitor_market_signals():
    """
    Tarea periódica que monitorea el mercado y envía alertas cuando hay consenso
    """
    try:
        # Ejecutar la tarea asíncrona
        result = asyncio.run(_check_and_alert())
        return result
    except Exception as e:
        print(f"❌ Error en monitor_market_signals: {e}")
        return {"status": "error", "message": str(e)}


async def _check_and_alert() -> dict:
    """
    Verifica si hay señal de consenso y envía alerta si es necesario
    """
    global _last_signal_sent
    
    settings = get_settings()
    symbol = settings.SYMBOL or "BTCUSDT"
    
    print(f"\n{'='*60}")
    print(f"🔍 Monitoreando {symbol} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # Crear controlador y obtener análisis
        controller = MultiTimeframeController(symbol=symbol)
        analysis = await controller.get_multi_timeframe_signal()
        
        consensus = analysis.get("consensus", {})
        signal = consensus.get("signal")
        confidence = consensus.get("confidence", 0)
        votes = analysis.get("votes", {})
        timeframes = analysis.get("timeframes", [])
        
        # Obtener precio actual
        current_price = None
        if timeframes:
            current_price = timeframes[0].get("price")
        
        print(f"💰 Precio: ${current_price}")
        print(f"🎯 Señal: {signal or 'None'} - Confianza: {confidence}%")
        print(f"📊 Votos: {votes.get('long', 0)} LONG, {votes.get('short', 0)} SHORT, {votes.get('neutral', 0)} NEUTRAL")
        
        # Verificar si hay señal con buena confianza
        if signal and confidence >= 50:
            # Verificar si es una señal nueva (evitar spam)
            should_send = _should_send_alert(signal, current_price, confidence)
            
            if should_send:
                print(f"📱 ¡Nueva señal detectada! Enviando alerta a Telegram...")
                
                # La alerta ya se envió en el controlador, solo registramos
                _last_signal_sent = {
                    "signal": signal,
                    "timestamp": datetime.now(),
                    "price": current_price,
                    "confidence": confidence
                }
                
                print(f"✅ Alerta enviada exitosamente")
                
                return {
                    "status": "alert_sent",
                    "signal": signal,
                    "confidence": confidence,
                    "price": current_price,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"⏭️  Señal ya enviada previamente, esperando cambio...")
                return {
                    "status": "already_alerted",
                    "signal": signal,
                    "confidence": confidence,
                    "price": current_price
                }
        else:
            print(f"⚪ Sin consenso suficiente - Esperando confirmación...")
            
            # Si no hay señal, resetear el registro
            if not signal:
                _last_signal_sent = {
                    "signal": None,
                    "timestamp": None,
                    "price": None
                }
            
            return {
                "status": "no_signal",
                "confidence": confidence,
                "price": current_price
            }
            
    except Exception as e:
        print(f"❌ Error al analizar mercado: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        print(f"{'='*60}\n")


def _should_send_alert(signal: str, price: Optional[float], confidence: float) -> bool:
    """
    Determina si se debe enviar una alerta basándose en la última señal enviada
    
    Criterios para enviar nueva alerta:
    1. Si es la primera señal (nunca se ha enviado una)
    2. Si cambió la dirección de la señal (LONG ↔ SHORT)
    3. Si pasaron más de 4 horas desde la última alerta de la misma señal
    4. Si la confianza aumentó significativamente (>15%) y el precio cambió >1%
    """
    global _last_signal_sent
    
    last_signal = _last_signal_sent.get("signal")
    last_timestamp = _last_signal_sent.get("timestamp")
    last_price = _last_signal_sent.get("price")
    last_confidence = _last_signal_sent.get("confidence", 0)
    
    # Primera señal
    if last_signal is None:
        return True
    
    # Cambió la dirección de la señal
    if signal != last_signal:
        return True
    
    # Si no hay timestamp previo, enviar
    if last_timestamp is None:
        return True
    
    # Calcular tiempo transcurrido
    time_diff = datetime.now() - last_timestamp
    hours_passed = time_diff.total_seconds() / 3600
    
    # Pasaron más de 4 horas con la misma señal
    if hours_passed > 4:
        return True
    
    # Mejoró significativamente la confianza y cambió el precio
    if price and last_price:
        confidence_increase = confidence - last_confidence
        price_change_pct = abs((price - last_price) / last_price * 100)
        
        if confidence_increase > 15 and price_change_pct > 1:
            return True
    
    # No cumple criterios para nueva alerta
    return False


@celery_app.task(name="app.celery_worker.tasks.test_telegram")
def test_telegram():
    """
    Tarea de prueba para verificar que Celery y Telegram funcionan
    """
    try:
        from app.services.telegram_service import TelegramService
        
        telegram = TelegramService()
        result = asyncio.run(telegram.send_message(
            "🤖 Test de Celery Worker\n\n"
            "✅ El sistema de monitoreo automático está funcionando correctamente.\n"
            f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ))
        
        return {
            "status": "success",
            "message": "Test message sent",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
