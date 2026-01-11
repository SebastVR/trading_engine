"""
Trading AI Agent: Validación de señales con inteligencia artificial
Fase 1: Filtro de calidad de signals usando Bedrock
"""

import json
import logging
from typing import Optional, Dict, Any

from app.services.bedrock_service import bedrock_service
from app.config.settings import settings


logger = logging.getLogger(__name__)


class TradingAIAgent:
    """Agente IA para validar y analizar señales de trading."""

    SYSTEM_PROMPT = """Eres un analista técnico senior especializado en trading y mercados financieros.

Tu expertise incluye:
- Estructura de mercado: BOS (Break of Structure), CHoCH, HH/HL, LH/LL
- Smart Money Concepts: Order Blocks, Fair Value Gaps, Liquidity Zones
- Price Action: patrones de velas, rechazos, impulsos y retrocesos
- Indicadores técnicos: medias móviles, RSI, ATR, Fibonacci
- Gestión de riesgo: R:R (Risk:Reward), posicionamiento de SL/TP

Principios core:
1. NO prometes ganancias - solo evalúas probabilidades
2. Análisis objetivo basado en datos técnicos
3. Gestión de riesgo PRIMERO
4. Confluencias sobre indicadores aislados
5. Respetas la dirección dominante del mercado

INSTRUCCIONES CRÍTICAS:
- Debes retornar ÚNICAMENTE un JSON válido
- NO incluyas tags XML/HTML como <reasoning>
- NO incluyas texto adicional antes o después del JSON
- El JSON debe ser válido y parseable
- Comienza directamente con { y termina con }

Responde EXACTAMENTE en este formato JSON:
{
  "quality_score": <0-100>,
  "confidence": <0-100>,
  "confluences": [<list of technical confirmations>],
  "risks": [<list of identified risks>],
  "recommendation": "<OPEN|WAIT|SKIP>",
  "reasoning": "<brief explanation>"
}"""

    def __init__(self):
        """Inicializa el agente."""
        self.bedrock = bedrock_service

    async def validate_signal(
        self,
        signal: Dict[str, Any],
        symbol: str,
        timeframe: str,
        market_context: Optional[Dict[str, Any]] = None,
        historical_win_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Valida una señal de trading y retorna score de calidad.

        Args:
            signal: Dict con {signal, entry, stop_loss, take_profit, confirmations}
            symbol: Par (Ej: BTCUSDT)
            timeframe: Timeframe (Ej: 15m, 1h, 4h)
            market_context: Contexto de mercado opcional
            historical_win_rate: Win rate histórico de signals similares

        Returns:
            Dict con {quality_score, confidence, confluences, risks, recommendation, reasoning}
        """
        try:
            logger.info(f"🤖 Iniciando validación signal | {symbol} | {signal.get('signal')}")
            
            # Preparar prompt para Bedrock
            prompt = self._build_validation_prompt(
                signal=signal,
                symbol=symbol,
                timeframe=timeframe,
                market_context=market_context,
                historical_win_rate=historical_win_rate,
            )

            logger.info(f"📤 Enviando signal a Bedrock para validación...")

            # Llamar a Bedrock
            response = self.bedrock.query_bedrock(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=settings.AI_TEMPERATURE_FILTER,
                max_tokens=settings.AI_MAX_TOKENS,
            )

            logger.info(f"📥 Respuesta de Bedrock ({len(response)} chars)")

            # Parsear respuesta JSON
            validation_result = self.bedrock.validate_json_response(response)

            # Agregar campos computed
            validation_result["signal_data"] = {
                "symbol": symbol,
                "timeframe": timeframe,
                "direction": signal.get("signal", "UNKNOWN"),
                "entry": signal.get("entry"),
                "sl": signal.get("stop_loss"),
                "tp": signal.get("take_profit"),
            }

            return validation_result

        except Exception as e:
            logger.error(f"❌ Error validando signal: {str(e)}")
            # Retornar resultado con score bajo en caso de error
            return {
                "quality_score": 0,
                "confidence": "low",
                "confluences": [],
                "risks": [f"Error en validación: {str(e)}"],
                "recommendation": "SKIP",
                "reasoning": f"Error interno al validar signal: {str(e)}",
                "error": True,
            }

    def _build_validation_prompt(
        self,
        signal: Dict[str, Any],
        symbol: str,
        timeframe: str,
        market_context: Optional[Dict[str, Any]] = None,
        historical_win_rate: Optional[float] = None,
    ) -> str:
        """Construye el prompt para validar signal."""

        signal_type = signal.get("signal", "UNKNOWN")
        entry = signal.get("entry")
        sl = signal.get("stop_loss")
        tp = signal.get("take_profit")
        confirmations = signal.get("confirmations", {})

        # Calcular R:R
        rr_ratio = 0.0
        if entry and sl and tp and signal_type:
            if signal_type.upper() == "LONG":
                risk = entry - sl
                reward = tp - entry
            else:  # SHORT
                risk = sl - entry
                reward = entry - tp

            if risk > 0:
                rr_ratio = reward / risk

        prompt = f"""Analiza el siguiente setup de trading y valida su calidad:

📊 INFORMACIÓN DEL SETUP
- Symbol: {symbol}
- Timeframe: {timeframe}
- Dirección: {signal_type.upper()}
- Precio de Entrada: ${entry:.2f}
- Stop Loss: ${sl:.2f}
- Take Profit: ${tp:.2f}
- Risk:Reward Ratio: {rr_ratio:.2f}:1

📈 CONFIRMACIONES DETECTADAS
{json.dumps(confirmations, indent=2, ensure_ascii=False)}
"""

        if market_context:
            prompt += f"""
🌍 CONTEXTO DE MERCADO
{json.dumps(market_context, indent=2, ensure_ascii=False)}
"""

        if historical_win_rate is not None:
            prompt += f"""
📊 HISTÓRICO
- Win Rate de setups similares: {historical_win_rate:.1f}%
"""

        prompt += """
🎯 SOLICITUD DE VALIDACIÓN

Analiza este setup considerando:
1. ¿Las confirmaciones son suficientes y coherentes? (mínimo 3 confluencias)
2. ¿El R:R justifica el riesgo? (mínimo 1:2.5)
3. ¿Hay confluencia entre estructura, precio y tendencia?
4. ¿Qué riesgos o señales contrarias existen?
5. ¿Es un setup de alta probabilidad según análisis técnico profesional?
6. ¿Qué tan confiado estás en esta evaluación?

RESPONDE EN JSON CON ESTE FORMATO (Y SOLO ESTO, SIN TEXTO ADICIONAL):
{
    "quality_score": <número 0-100>,
    "confidence": "<low|medium|high>",
    "confluences": [
        "confluencia 1",
        "confluencia 2",
        "confluencia 3"
    ],
    "risks": [
        "riesgo 1",
        "riesgo 2"
    ],
    "rr_evaluation": "texto evaluando el R:R",
    "recommendation": "<OPEN|WAIT|SKIP>",
    "reasoning": "explicación breve de por qué este score",
    "key_insight": "insight técnico más importante"
}

NOTAS IMPORTANTES:
- quality_score: 0-30=SKIP, 30-75=WAIT, 75-100=OPEN
- Sé crítico: un score de 100 es muy raro
- Si faltan datos, penaliza el score
- Siempre prioriza gestión de riesgo
"""

        return prompt

    async def should_open_trade(self, quality_score: float) -> bool:
        """Determina si debe abrirse un trade basado en el score."""
        threshold = settings.AI_QUALITY_THRESHOLD
        return quality_score >= threshold

    def get_score_color(self, quality_score: float) -> str:
        """Retorna emoji basado en score."""
        if quality_score >= 75:
            return "🟢"  # GREEN - OPEN
        elif quality_score >= 50:
            return "🟡"  # YELLOW - WAIT
        else:
            return "🔴"  # RED - SKIP


# Instancia global del agente
trading_ai_agent = TradingAIAgent()
