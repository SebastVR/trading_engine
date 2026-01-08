import json
from typing import Optional

from app.config.settings import settings


class TradingAIAgent:
    """Agente de IA experto en análisis técnico y trading."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self._client = None

    def _init_gemini(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no configurada")
        
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Usar gemini-1.5-pro-latest que es estable y funciona con la API actual
        self._client = genai.GenerativeModel('gemini-1.5-pro-latest')

    def _init_openai(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no configurada")
        
        from langchain_openai import ChatOpenAI
        self._client = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.AI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )

    async def analyze_signal(
        self,
        signal: dict,
        symbol: str,
        timeframe: str,
        market_context: Optional[dict] = None
    ) -> Optional[str]:
        if not settings.AI_ENABLED:
            return None

        try:
            if self.provider == "gemini":
                return await self._analyze_with_gemini(signal, symbol, timeframe, market_context)
            elif self.provider == "openai":
                return await self._analyze_with_openai(signal, symbol, timeframe, market_context)
            else:
                return f"Proveedor de IA no soportado: {self.provider}"
        except Exception as e:
            return f"Error en análisis de IA: {str(e)}"

    async def _analyze_with_gemini(self, signal: dict, symbol: str, timeframe: str, market_context: Optional[dict]) -> str:
        if not self._client:
            self._init_gemini()

        prompt = self._build_expert_prompt(signal, symbol, timeframe, market_context)
        response = self._client.generate_content(prompt)
        return response.text

    async def _analyze_with_openai(self, signal: dict, symbol: str, timeframe: str, market_context: Optional[dict]) -> str:
        if not self._client:
            self._init_openai()

        from langchain_core.prompts import ChatPromptTemplate

        template = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{analysis_request}")
        ])

        prompt = self._build_expert_prompt(signal, symbol, timeframe, market_context)
        messages = template.format_messages(analysis_request=prompt)
        response = self._client.invoke(messages)
        return response.content

    def _get_system_prompt(self) -> str:
        return """Eres un analista técnico senior especializado en trading y mercados financieros.

Tu expertise incluye:
- Estructura de mercado: BOS, CHoCH, HH/HL, LH/LL
- Smart Money Concepts: Order Blocks, Fair Value Gaps, Liquidity Zones
- Price Action: patrones de velas, rechazos, impulsos y retrocesos
- Indicadores técnicos: medias móviles, RSI, ATR, Fibonacci
- Gestión de riesgo: R:R, posicionamiento de SL/TP

Principios:
1. NO prometes ganancias - solo evalúas probabilidades
2. Análisis objetivo basado en datos
3. Gestión de riesgo primero
4. Confluencias sobre indicadores aislados
5. Respetas la dirección dominante

Formato de respuesta:
- Calidad del Setup: [1-10]
- Confluencias Detectadas: [lista]
- Riesgos Identificados: [lista]
- Alineación con Tendencia: [sí/no/neutral]
- Recomendación: [texto breve]
- Nivel de Confianza: [bajo/medio/alto]

Máximo 250 palabras."""

    def _build_expert_prompt(self, signal: dict, symbol: str, timeframe: str, market_context: Optional[dict]) -> str:
        signal_type = signal.get("signal", "None")
        reason = signal.get("reason", {})
        entry = signal.get("entry")
        sl = signal.get("stop_loss")
        tp = signal.get("take_profit")

        # Si no hay señal, devolver análisis de mercado general
        if not signal_type or signal_type == "None":
            return f"""Análisis de mercado para {symbol} ({timeframe}):

No hay setup válido en este momento.
Motivo: {json.dumps(reason, indent=2, ensure_ascii=False)}

Contexto de mercado: {json.dumps(market_context, indent=2, ensure_ascii=False) if market_context else "No disponible"}

Mantén paciencia y espera confirmaciones claras."""

        rr_ratio = 0.0
        if entry and sl and tp and signal_type:
            if signal_type == "long":
                risk = entry - sl
                reward = tp - entry
            else:
                risk = sl - entry
                reward = entry - tp
            
            if risk > 0:
                rr_ratio = reward / risk

        prompt = f"""Analiza el siguiente setup de trading:

📊 INFORMACIÓN DEL TRADE
Symbol: {symbol}
Timeframe: {timeframe}
Dirección: {signal_type.upper()}
Precio de Entrada: {entry:.2f} USD
Stop Loss: {sl:.2f} USD
Take Profit: {tp:.2f} USD
Risk:Reward Ratio: {rr_ratio:.2f}

📈 CONFIRMACIONES DETECTADAS
{json.dumps(reason, indent=2, ensure_ascii=False)}
"""

        if market_context:
            prompt += f"\n🌍 CONTEXTO DE MERCADO\n{json.dumps(market_context, indent=2, ensure_ascii=False)}\n"

        prompt += """
🎯 SOLICITUD DE ANÁLISIS
Evalúa este setup considerando:
1. ¿Las confirmaciones son suficientes y coherentes?
2. ¿El R:R justifica el riesgo?
3. ¿Hay confluencia entre estructura, precio y tendencia?
4. ¿Qué riesgos o señales contrarias existen?
5. ¿Es un setup de alta probabilidad según análisis técnico profesional?

Proporciona tu análisis siguiendo el formato establecido."""

        return prompt


class AIService:
    """Servicio principal de IA para el motor de trading."""

    def __init__(self):
        self.agent = TradingAIAgent()

    async def analyze_signal(
        self,
        signal: dict,
        symbol: str,
        timeframe: str,
        market_context: Optional[dict] = None
    ) -> Optional[str]:
        if not settings.AI_ENABLED:
            return None
        
        if not settings.GEMINI_API_KEY and not settings.OPENAI_API_KEY:
            return "IA habilitada pero falta configurar API keys (GEMINI_API_KEY o OPENAI_API_KEY)"

        return await self.agent.analyze_signal(signal, symbol, timeframe, market_context)
