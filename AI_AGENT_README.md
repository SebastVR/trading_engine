# Trading Engine - Sistema de IA (Agente Experto)

## 🤖 Descripción

El motor de trading incluye un **agente de IA experto** en análisis técnico y mercados financieros que actúa como **copiloto** para validar y mejorar la calidad de los setups de trading.

### ⚠️ Importante
- La IA **NO ejecuta trades automáticamente**
- Solo **analiza y valida** los setups generados
- Proporciona un **segundo opinion** basado en análisis técnico profesional
- Identifica **riesgos** y **confluencias** que podrías pasar por alto

---

## 🎯 Capacidades del Agente

El agente de IA está entrenado para analizar:

### 📊 Estructura de Mercado
- **BOS** (Break of Structure)
- **CHoCH** (Change of Character)
- **HH/HL** (Higher Highs / Higher Lows) - tendencia alcista
- **LH/LL** (Lower Highs / Lower Lows) - tendencia bajista

### 💎 Smart Money Concepts
- **Order Blocks** (zonas de liquidez institucional)
- **Fair Value Gaps** (huecos de valor justo)
- **Liquidity Zones** (zonas de liquidez)

### 🕯️ Price Action
- Patrones de velas japonesas
- Rechazos en niveles clave
- Impulsos y retrocesos
- Confirmaciones de cierre

### 📈 Indicadores Técnicos
- Medias móviles (MA/EMA)
- RSI (Relative Strength Index)
- ATR (Average True Range)
- Retrocesos de Fibonacci

### 🛡️ Gestión de Riesgo
- Validación de R:R (Risk:Reward)
- Posicionamiento de SL/TP
- Evaluación de riesgo vs recompensa

---

## 🔧 Configuración

### 1. Proveedores Soportados

#### Google Gemini (Recomendado - FREE)
- **Modelo**: `gemini-1.5-pro`
- **Ventajas**: 
  - API gratuita con límites generosos
  - Excelente calidad de análisis
  - Respuestas rápidas
- **Cómo obtener tu API Key**:
  1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Crea una API key
  3. Cópiala a tu `.env`

#### OpenAI (Alternativa)
- **Modelos**: `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`
- **Ventajas**:
  - Alta calidad de análisis
  - Respuestas muy estructuradas
- **Desventajas**:
  - Requiere pago por uso
- **Cómo obtener tu API Key**:
  1. Ve a [OpenAI Platform](https://platform.openai.com/api-keys)
  2. Crea una API key
  3. Cópiala a tu `.env`

### 2. Variables de Entorno

Edita tu archivo `.env`:

```bash
# IA Configuration
AI_ENABLED=true
AI_PROVIDER=gemini  # gemini | openai

# Gemini (recomendado)
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-1.5-pro

# OpenAI (alternativa)
OPENAI_API_KEY=tu_clave_aqui
OPENAI_MODEL=gpt-4o-mini

# Temperatura (creatividad del modelo)
AI_TEMPERATURE=0.2  # 0.0 = más determinístico, 1.0 = más creativo
```

### 3. Instalación de Dependencias

El archivo `requirements.txt` ya incluye las librerías necesarias:

```bash
# Para Gemini
google-generativeai==0.8.3

# Para OpenAI
langchain==0.3.13
langchain-core==0.3.27
langchain-openai==0.2.14
```

Si necesitas reinstalar:

```bash
pip install -r requirements.txt
```

O con Docker (recomendado):

```bash
docker compose build
docker compose up
```

---

## 📝 Formato de Análisis

El agente devuelve un análisis estructurado con:

### Ejemplo de Respuesta

```
Calidad del Setup: 7/10

Confluencias Detectadas:
✅ Tendencia alcista confirmada (MA20 > MA50)
✅ Ruptura de estructura (BOS) en zona de demanda
✅ RSI en zona neutral (45-70)
✅ R:R de 2.5:1 - favorable

Riesgos Identificados:
⚠️ ATR elevado - aumenta volatilidad
⚠️ Volumen por debajo del promedio - debilita confirmación
⚠️ Cercanía al máximo reciente - posible rechazo

Alineación con Tendencia: Sí
- Precio por encima de EMA200
- Estructura de Higher Highs intacta

Recomendación:
Setup válido con buenas confluencias. Considera esperar 
confirmación adicional (cierre de vela) antes de entrada.
El R:R es favorable pero vigila el volumen.

Nivel de Confianza: Medio-Alto
```

---

## 🚀 Uso en el Código

### Opción 1: Análisis Automático en Señales

El agente se ejecuta automáticamente cuando se genera una señal:

```python
# En trade_controller.py
signal = strategy.compute_signal(df)

if settings.AI_ENABLED:
    ai_note = await ai.analyze_signal(
        signal=signal,
        symbol=settings.SYMBOL,
        timeframe=settings.TIMEFRAME,
        market_context=market_context
    )
    signal["ai_note"] = ai_note
```

### Opción 2: Análisis Manual

```python
from app.services.ai_service import AIService

ai = AIService()

signal = {
    "signal": "long",
    "entry": 95000,
    "stop_loss": 94000,
    "take_profit": 97000,
    "reason": {
        "trend": "up",
        "breakout": "close > high(20)",
        "rsi": 55.2
    }
}

market_context = {
    "current_price": 95000,
    "recent_high": 96000,
    "recent_low": 93000,
    "volume_avg": 1500000
}

analysis = await ai.analyze_signal(
    signal=signal,
    symbol="BTCUSDT",
    timeframe="1h",
    market_context=market_context
)

print(analysis)
```

---

## 🔍 Arquitectura del Agente

```
AIService (facade)
    └── TradingAIAgent
            ├── _init_gemini()
            ├── _init_openai()
            ├── analyze_signal()
            ├── _analyze_with_gemini()
            ├── _analyze_with_openai()
            ├── _get_system_prompt()
            └── _build_expert_prompt()
```

### Flujo de Análisis

1. **Recepción**: Recibe señal + contexto de mercado
2. **Preparación**: Construye prompt experto con todos los datos
3. **Análisis**: Envía a Gemini/OpenAI según configuración
4. **Respuesta**: Devuelve análisis estructurado en español
5. **Almacenamiento**: Se guarda en campo `ai_note` del trade

---

## 💡 Mejores Prácticas

### 1. Contexto de Mercado Rico
Proporciona siempre que sea posible:
- Precio actual
- Máximos/mínimos recientes
- Volumen promedio
- Niveles clave (soportes/resistencias)
- Tendencia del timeframe superior

### 2. Temperatura del Modelo
- **0.0 - 0.3**: Análisis consistente y determinístico (recomendado para trading)
- **0.4 - 0.7**: Balance entre creatividad y consistencia
- **0.8 - 1.0**: Respuestas más creativas pero menos predecibles

### 3. Validación Humana
- **Siempre revisa** el análisis de la IA
- **No operes a ciegas** basándote solo en la IA
- Usa la IA como **segunda opinión**, no como decisión final

### 4. Costos
- **Gemini**: ~15 llamadas/minuto gratis, luego límites por día
- **OpenAI**: Pago por token (gpt-4o-mini es económico, ~$0.15/1M tokens)

---

## 🐛 Troubleshooting

### Error: "IA habilitada pero falta configurar API keys"
**Solución**: Verifica que tienes `GEMINI_API_KEY` o `OPENAI_API_KEY` en tu `.env`

### Error: "ModuleNotFoundError: No module named 'google.generativeai'"
**Solución**: 
```bash
pip install google-generativeai
# O reconstruye el contenedor
docker compose build
```

### Error: "CERTIFICATE_VERIFY_FAILED"
**Solución**: Ya está resuelto en el Dockerfile con `ca-certificates`

### La IA devuelve análisis muy genéricos
**Solución**: 
- Proporciona más contexto en `market_context`
- Ajusta la temperatura a un valor más bajo (0.1 - 0.2)
- Asegúrate de que el `signal` contenga todas las confirmaciones

---

## 📊 Ejemplo Completo de Flujo

```bash
# 1. Configurar .env
AI_ENABLED=true
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...

# 2. Levantar proyecto
docker compose up --build

# 3. Consultar señal (incluye análisis IA)
curl http://localhost/api/signals/latest

# Respuesta:
{
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "signal": "long",
  "entry": 95234.50,
  "stop_loss": 94500.00,
  "take_profit": 96700.00,
  "reason": {...},
  "ai_note": "Calidad del Setup: 8/10\n\nConfluencias Detectadas:..."
}
```

---

## 🎓 Referencias y Learning

### Videos Recomendados
- [Trading con IA y Market Structure](https://www.youtube.com/watch?v=jz0tYDhI7eU&t=12s)
- [Smart Money Concepts Explicados](https://www.youtube.com/watch?v=zQiBg8MC8IM&t=2s)

### Conceptos de Trading
- **BOS/CHoCH**: ICT (Inner Circle Trader) concepts
- **Order Blocks**: Smart Money Concepts
- **Price Action**: Al Brooks, Steve Nison
- **Gestión de Riesgo**: Van K. Tharp

---

## 🔮 Roadmap Futuro

- [ ] Análisis de múltiples timeframes
- [ ] Detección automática de Order Blocks
- [ ] Backtesting con validación de IA
- [ ] Journal automático con feedback de IA
- [ ] Integración con más proveedores (Claude, Llama local)
- [ ] Dashboard de métricas de IA vs trading manual

---

## ⚖️ Disclaimer

Este sistema es **educativo y de investigación**. La IA puede cometer errores y **no garantiza ganancias**. Trading con criptomonedas implica riesgo alto. Siempre:
- Practica en paper trading primero
- Usa gestión de riesgo estricta
- No arriesgues más del 1-2% por operación
- Consulta con asesores financieros si es necesario

---

**¿Preguntas o mejoras?**
- Abre un issue en el repositorio
- Consulta la documentación en `/trading_engine_contexto_prompt.md`
