"""
Telegram Alert Service
Envía notificaciones de trading a Telegram
"""

import httpx
from typing import Optional
from app.config.settings import settings


class TelegramService:
    """
    Servicio para enviar alertas a Telegram
    """
    
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        self.enabled = self.bot_token and self.chat_id
    
    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Envía un mensaje a Telegram
        
        Args:
            message: Texto del mensaje (soporta HTML)
            parse_mode: "HTML" o "Markdown"
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.enabled:
            print("⚠️  Telegram no configurado. Mensaje no enviado:")
            print(message)
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                print(f"✅ Mensaje enviado a Telegram (chat_id: {self.chat_id})")
                return True
                
        except Exception as e:
            print(f"❌ Error enviando mensaje a Telegram: {e}")
            return False
    
    async def send_signal_alert(
        self,
        symbol: str,
        signal_type: str,
        confidence: float,
        price: float,
        entry: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        timeframe: Optional[str] = None
    ) -> bool:
        """
        Envía alerta de señal de trading
        """
        if signal_type == "LONG":
            icon = "🟢"
            action = "COMPRAR"
        elif signal_type == "SHORT":
            icon = "🔴"
            action = "VENDER"
        else:
            icon = "⚪"
            action = "NEUTRAL"
        
        message = f"""
{icon} <b>SEÑAL DE TRADING</b> {icon}

<b>Par:</b> {symbol}
<b>Acción:</b> {action} ({signal_type})
<b>Confianza:</b> {confidence:.1f}%
<b>Precio Actual:</b> ${price:,.2f}
"""
        
        if timeframe:
            message += f"<b>Timeframe:</b> {timeframe}\n"
        
        if entry:
            message += f"\n<b>💰 Setup de Trading:</b>\n"
            message += f"  • Entry: ${entry:,.2f}\n"
            
            if stop_loss:
                risk = abs(entry - stop_loss)
                risk_pct = (risk / entry) * 100
                message += f"  • Stop Loss: ${stop_loss:,.2f} (-{risk_pct:.2f}%)\n"
            
            if take_profit:
                reward = abs(take_profit - entry)
                reward_pct = (reward / entry) * 100
                message += f"  • Take Profit: ${take_profit:,.2f} (+{reward_pct:.2f}%)\n"
            
            if stop_loss and take_profit:
                rr = abs(take_profit - entry) / abs(entry - stop_loss)
                message += f"  • R:R = 1:{rr:.2f}\n"
        
        message += f"\n⏰ <i>{self._get_timestamp()}</i>"
        
        return await self.send_message(message)
    
    async def send_multi_timeframe_alert(
        self,
        symbol: str,
        consensus_signal: Optional[str],
        confidence: float,
        long_votes: int,
        short_votes: int,
        neutral_votes: int,
        weighted_score: float,
        price: float,
        entry: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """
        Envía alerta de consenso multi-timeframe
        """
        if consensus_signal == "LONG":
            icon = "🟢"
            action = "COMPRAR"
        elif consensus_signal == "SHORT":
            icon = "🔴"
            action = "VENDER"
        else:
            icon = "⚪"
            action = "SIN CONSENSO"
        
        message = f"""
{icon} <b>CONSENSO MULTI-TIMEFRAME</b> {icon}

<b>Par:</b> {symbol}
<b>Decisión:</b> {action}
<b>Confianza:</b> {confidence:.1f}%
<b>Score Ponderado:</b> {weighted_score:+.1f}

<b>📊 Votos por Timeframe:</b>
  • LONG: {long_votes}
  • SHORT: {short_votes}
  • NEUTRAL: {neutral_votes}

<b>Precio Actual:</b> ${price:,.2f}
"""
        
        if consensus_signal and entry:
            message += f"\n<b>💰 Setup Recomendado:</b>\n"
            message += f"  • Entry: ${entry:,.2f}\n"
            
            if stop_loss:
                risk = abs(entry - stop_loss)
                risk_pct = (risk / entry) * 100
                message += f"  • Stop Loss: ${stop_loss:,.2f} (-{risk_pct:.2f}%)\n"
            
            if take_profit:
                reward = abs(take_profit - entry)
                reward_pct = (reward / entry) * 100
                message += f"  • Take Profit: ${take_profit:,.2f} (+{reward_pct:.2f}%)\n"
            
            if stop_loss and take_profit:
                rr = abs(take_profit - entry) / abs(entry - stop_loss)
                message += f"  • R:R = 1:{rr:.2f}\n"
        
        message += f"\n⏰ <i>{self._get_timestamp()}</i>"
        
        return await self.send_message(message)
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp formateado"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
