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
    
    async def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
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
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code != 200:
                    print(f"❌ Error Telegram ({response.status_code}): {response.text}")
                    return False
                
                print(f"✅ Mensaje enviado a Telegram (chat_id: {self.chat_id})")
                return True
                
        except Exception as e:
            print(f"❌ Error enviando mensaje a Telegram: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_signal_alert(
        self,
        symbol: str,
        signal_type: str,
        price: float,
        entry: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        timeframe: Optional[str] = None,
        reason: Optional[str] = None,
        confidence: float = 0.0
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
        
        # Construir mensaje línea por línea SIN HTML para evitar errores de parsing
        lines = []
        lines.append(f"{icon} SEÑAL DE TRADING {icon}")
        lines.append(f"Par: {symbol}")
        lines.append(f"Acción: {action} ({signal_type})")
        lines.append(f"Confianza: {confidence:.1f}%")
        lines.append(f"Precio Actual: ${price:,.2f}")
        
        if reason:
            lines.append(f"Razón: {reason}")
        
        if timeframe:
            lines.append(f"Timeframe: {timeframe}")
        
        if entry:
            lines.append("💰 Setup de Trading:")
            lines.append(f"  • Entry: ${entry:,.2f}")
            
            if stop_loss:
                risk = abs(entry - stop_loss)
                risk_pct = (risk / entry) * 100
                lines.append(f"  • Stop Loss: ${stop_loss:,.2f} (-{risk_pct:.2f}%)")
            
            if take_profit:
                reward = abs(take_profit - entry)
                reward_pct = (reward / entry) * 100
                lines.append(f"  • Take Profit: ${take_profit:,.2f} (+{reward_pct:.2f}%)")
            
            if stop_loss and take_profit:
                rr = abs(take_profit - entry) / abs(entry - stop_loss)
                lines.append(f"  • R:R = 1:{rr:.2f}")
        
        message = "\n".join(lines)
        
        message += f"\n⏰ {self._get_timestamp()}"
        
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
        
        # Construir mensaje línea por línea SIN HTML para evitar errores de parsing
        lines = []
        lines.append(f"{icon} CONSENSO MULTI-TIMEFRAME {icon}")
        lines.append(f"Par: {symbol}")
        lines.append(f"Decisión: {action}")
        lines.append(f"Confianza: {confidence:.1f}%")
        lines.append(f"Score Ponderado: {weighted_score:+.1f}")
        lines.append("📊 Votos por Timeframe:")
        lines.append(f"  • LONG: {long_votes}")
        lines.append(f"  • SHORT: {short_votes}")
        lines.append(f"  • NEUTRAL: {neutral_votes}")
        lines.append(f"Precio Actual: ${price:,.2f}")
        
        if consensus_signal and entry:
            lines.append("💰 Setup Recomendado:")
            lines.append(f"  • Entry: ${entry:,.2f}")
            
            if stop_loss:
                risk = abs(entry - stop_loss)
                risk_pct = (risk / entry) * 100
                lines.append(f"  • Stop Loss: ${stop_loss:,.2f} (-{risk_pct:.2f}%)")
            
            if take_profit:
                reward = abs(take_profit - entry)
                reward_pct = (reward / entry) * 100
                lines.append(f"  • Take Profit: ${take_profit:,.2f} (+{reward_pct:.2f}%)")
            
            if stop_loss and take_profit:
                rr = abs(take_profit - entry) / abs(entry - stop_loss)
                lines.append(f"  • R:R = 1:{rr:.2f}")
        
        message = "\n".join(lines)
        
        message += f"\n⏰ {self._get_timestamp()}"
        
        return await self.send_message(message)
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp formateado en hora de Colombia (UTC-5)"""
        from datetime import datetime, timezone, timedelta
        # Colombia está en UTC-5
        colombia_tz = timezone(timedelta(hours=-5))
        return datetime.now(colombia_tz).strftime("%Y-%m-%d %H:%M:%S Colombia")
