# Trading Engine (BTCUSDT) — Contexto completo + Prompt maestro (FastAPI + Postgres + Alertas + IA)

> **Aviso importante (no es asesoría financiera):** Este proyecto es **educativo y de investigación**. Ninguna estrategia garantiza ganancias. Operar con cripto/forex implica riesgo alto. Antes de usarlo con dinero real: backtesting, paper trading, validación estadística, límites de riesgo y cumplimiento normativo.

## 1) Objetivo del proyecto

Construir un **motor de trading en tiempo real** para **BTCUSDT** que:

- Analice múltiples **confirmaciones** (estructura, tendencia, acción del precio, medias móviles, Fibonacci, velas/patrones).
- Genere **alertas de entrada** con:
  - dirección (LONG/SHORT),
  - zona de entrada,
  - **Stop Loss** y **Take Profit** (obligatorios),
  - razones/confirmaciones.
- Registre cada operación en **PostgreSQL** y, cuando el precio toque SL/TP o cierre por regla, envíe una **segunda notificación** indicando si se **ganó o se perdió**, incluyendo el **precio real de cierre**.
- Exponga un **API GET** para ver un **resumen tabular** de todas las operaciones (entrada, SL, TP, precio cierre, resultado, timeframe, timestamp), para cortes semanales/mensuales.
- Permita cambiar **temporalidad**: 15m, 1h, 1d, 1w (y otras compatibles).
- Sea desplegable con **Dockerfile + docker-compose**, con `requirements.txt` a nivel raíz.
- Mantenga un espacio para **Inteligencia Artificial (IA)** (agente con LangChain) para **mejorar la toma de decisiones**, sin que la IA “controle” directamente el trading en producción sin validación.

---

## 2) Plataforma de datos y ejecución en tiempo real

### 2.1 Fuente de mercado (BTCUSDT)
- **Binance Spot**:
  - Para histórico: REST (klines/candles).
  - Para tiempo real: **WebSocket** (kline stream por símbolo y timeframe).
- Las variables:
  - `BINANCE_API_KEY`
  - `BINANCE_API_SECRET`
  provienen de tu cuenta de Binance en **API Management**. Se guardan en `.env` (no se suben a git).

> Nota: para **solo leer datos** y generar alertas, podrías operar sin llaves en ciertos endpoints públicos, pero **para órdenes** sí necesitas llaves.

### 2.2 Visualización (sin TradingView)
TradingView no se integra oficialmente para “pintar” overlays desde Python de forma nativa. Para pruebas y visualización local:

- Generar gráfico con **Plotly** (candles) y dibujar:
  - zonas de entrada,
  - SL/TP,
  - niveles Fibonacci,
  - medias móviles,
  - estructura (swing highs/lows).
- Exponer endpoint `GET /charts/latest` que devuelva:
  - imagen PNG (o HTML) del gráfico
  - con las marcas de la última señal.

Así puedes **validar visualmente** la estrategia en local o en un server sin depender de TradingView.

---

## 3) Estrategia: confirmaciones inspiradas en libros de trading (guía conceptual)

> **No se copia contenido** de libros; se usa como **marco conceptual** para elegir confirmaciones robustas.

### 3.1 “Estructura y Tendencia”
Confirmaciones típicas (inspiradas en enfoques de estructura/price action):
- **Higher High / Higher Low (HH/HL)** → sesgo alcista.
- **Lower High / Lower Low (LH/LL)** → sesgo bajista.
- **Break of Structure (BOS)** y **Change of Character (CHoCH)** para detectar cambio de sesgo.
- Zonas de oferta/demanda (supply/demand) derivadas de swings + velas impulsivas.

**Referencias (marco):**
- Al Brooks — *Trading Price Action* (conceptos de acción del precio y estructura).
- John J. Murphy — *Technical Analysis of the Financial Markets* (tendencia, soportes/resistencias).
- Mark Douglas — *Trading in the Zone* (disciplina y gestión psicológica).

### 3.2 “Acción del precio (Price Action)”
- Rechazos en niveles (wick rejection).
- Impulsos vs retrocesos.
- Rangos (consolidación) vs tendencia.
- Confirmación por **cierre** (close) y no solo por mechas.

**Referencias (marco):**
- Al Brooks — *Trading Price Action* (patrones y lectura de velas).
- Steve Nison — *Japanese Candlestick Charting Techniques* (velas y señales).

### 3.3 “Medias móviles (tendencia y filtro)”
- EMA 20/50/200 como filtros:
  - Sesgo alcista si precio > EMA200 y EMA20>EMA50.
  - Sesgo bajista si precio < EMA200 y EMA20<EMA50.
- Cruces (con cuidado): usados solo como confirmación, no como gatillo principal.

**Referencias (marco):**
- John J. Murphy — TA clásico (promedios y confirmación de tendencia).

### 3.4 “Fibonacci (zonas de retroceso/objetivos)”
- Retrocesos frecuentes: 38.2%, 50%, 61.8%.
- Confluencia:
  - Fib + estructura + PA (rechazo) + filtro de tendencia.

**Referencias (marco):**
- Murphy (TA) y práctica popular de confluencias.

### 3.5 “Tipos de velas y patrones”
- Pin bar / hammer / shooting star (rechazo).
- Engulfing (envolvente).
- Inside bar (compresión → ruptura).
- Marubozu (impulso fuerte).
> Importante: se evalúan **en contexto** (estructura + tendencia + nivel).

**Referencias (marco):**
- Steve Nison — velas japonesas.

### 3.6 “Gestión del riesgo (obligatoria)”
- Cada entrada define:
  - **Stop Loss** lógico (estructura: debajo/encima de swing).
  - **Take Profit** (R:R mínimo, p.ej. 1.5R o 2R).
- Riesgo por operación:
  - 0.5%–2% del capital (configurable).
- Control de costos:
  - Fee por operación configurable (maker/taker) en settings.
  - El cálculo de PnL incluye fees.

**Referencias (marco):**
- Van K. Tharp — *Trade Your Way to Financial Freedom* (posición y riesgo).
- Mark Douglas — disciplina y consistencia.

---

## 4) Dónde entra la Inteligencia Artificial (IA) y por qué

La IA **no debe** ser el gatillo final “a ciegas” sin validación. Usos recomendados y seguros:

1. **Agente de “Journaling & Post-Trade Review” (LangChain)**
   - Entrada: señal generada + confirmaciones + captura del gráfico + resultado (win/loss) + condiciones.
   - Salida:
     - explicación en lenguaje natural,
     - checklist de calidad (¿hubo confluencia real?),
     - sugerencias para reglas (p.ej. “filtrar señales contra EMA200”),
     - detectar “errores humanos” o “señales de baja calidad”.

2. **Agente de “Optimización de reglas” (offline)**
   - Analiza estadísticas por timeframe:
     - winrate, profit factor, drawdown, expectancy.
   - Propone ajustes (sin tocar producción):
     - thresholds, R:R, filtros adicionales.
   - Requiere dataset histórico y backtesting.

3. **Control de costos**
   - Registrar y estimar:
     - fees por operación,
     - slippage estimado,
     - impacto por frecuencia de trading.
   - IA puede recomendar reducir sobreoperación (“overtrading”) según métricas.

> En producción, el motor puede funcionar con reglas determinísticas; la IA ayuda como “copiloto” de análisis y aprendizaje continuo.

---

## 5) API y flujo del sistema

### 5.1 Flujo en tiempo real (simplificado)
1) `market_service` abre WebSocket a Binance para BTCUSDT + timeframe.
2) Cada vez que cierra una vela:
   - actualiza indicadores,
   - evalúa confirmaciones,
   - si hay señal → crea `Trade` con status `OPEN`, calcula SL/TP, guarda en Postgres, envía alerta.
3) En cada tick/vela:
   - evalúa si el precio tocó SL/TP,
   - si cerró → actualiza status `WON/LOST`, guarda `close_price`, envía alerta de resultado.
4) API permite consultar:
   - lista tabular de operaciones,
   - métricas agregadas por rango de fechas/timeframe,
   - gráfico de última señal.

### 5.2 Endpoints FastAPI (propuestos)
- `GET /health` → estado del servicio.
- `GET /trades` → tabla de operaciones (filtros: timeframe, date_from, date_to, status).
- `GET /trades/summary` → métricas agregadas (semana/mes).
- `GET /signals/latest` → última señal generada.
- `GET /charts/latest` → gráfico (PNG/HTML) con señales y SL/TP.

---

## 6) Estructura final del repositorio (proyecto)

```text
trading_engine/
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ .env
└─ app/
   ├─ main.py
   │
   ├─ config/
   │  ├─ __init__.py
   │  └─ settings.py
   │
   ├─ controllers/
   │  ├─ __init__.py
   │  ├─ trade_controller.py
   │  └─ health_controller.py
   │
   ├─ routers/
   │  ├─ __init__.py
   │  └─ trade_router.py
   │
   ├─ schemas/
   │  ├─ __init__.py
   │  └─ trade_schema.py
   │
   ├─ db/
   │  ├─ __init__.py
   │  ├─ session.py
   │  └─ migrations/        # opcional (Alembic después)
   │
   ├─ models/
   │  ├─ __init__.py
   │  └─ trade_model.py
   │
   ├─ enums/
   │  ├─ __init__.py
   │  └─ trade_enums.py
   │
   ├─ services/
   │  ├─ __init__.py
   │  ├─ trade_manager.py
   │  ├─ alert_service.py
   │  ├─ chart_service.py
   │  └─ market_service.py
   │
   ├─ celery_worker/
   │  ├─ __init__.py
   │  └─ worker.py           # futuro: backtest, reports
   │
   ├─ middleware/
   │  ├─ __init__.py
   │  └─ logging.py
   │
   ├─ util/
   │  ├─ __init__.py
   │  ├─ timeframes.py
   │  └─ math.py
```

---

## 7) Configuración (ejemplo de variables .env)

```bash
# App
APP_ENV=local
LOG_LEVEL=INFO

# Postgres
POSTGRES_DB=trading
POSTGRES_USER=trading
POSTGRES_PASSWORD=trading
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Binance (si vas a enviar órdenes en el futuro)
BINANCE_API_KEY=tu_api_key
BINANCE_API_SECRET=tu_api_secret

# Trading
SYMBOL=BTCUSDT
TIMEFRAME=15m
RISK_PER_TRADE=0.01
RR_MIN=2.0
FEE_RATE=0.001   # configurable; no asumir fijo
SLIPPAGE=0.0005  # configurable

# Alertas
ALERT_WEBHOOK_URL= # opcional (Discord/Slack/Teams)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# IA (opcional)
LLM_PROVIDER=none   # none|openai|bedrock|local
LLM_MODEL=
LLM_TEMPERATURE=0.2
```

---

## 8) Componentes clave del motor (qué construir a continuación)

### 8.1 Núcleo (reglas determinísticas)
- Detectar swings / estructura.
- Determinar sesgo (trend filter) con EMA200 y estructura.
- Confluencia:
  - estructura + fib + patrón de vela + MA + ruptura/confirmación.
- Generar trade:
  - entry (zona),
  - stop (por swing),
  - take profit (por R:R y/o nivel).

### 8.2 Seguimiento de trade y resultado (win/loss)
- Verificar en tiempo real:
  - si `low <= SL` → LOST,
  - si `high >= TP` → WON,
  - actualizar en DB + alerta.
- Guardar:
  - `close_price`,
  - `close_time`,
  - `pnl`,
  - `fees_paid`.

### 8.3 Reporte tabular y cortes
- API `GET /trades` con filtros.
- `GET /trades/summary` por rango:
  - total trades, winrate, net pnl, avg R, fees.

### 8.4 IA (copiloto)
- Post-trade review con LangChain:
  - Genera “reporte” por trade (texto).
- Recomendación de ajustes (offline):
  - Analiza histórico de trades y propone cambios.

---

## 9) Prompt maestro (para un nuevo chat)

Copia/pega lo siguiente en un chat nuevo para retomar el proyecto sin perder contexto:

```text
Estoy construyendo un proyecto llamado "trading_engine" en Python con FastAPI + PostgreSQL, dockerizado (Dockerfile + docker-compose + requirements.txt). El objetivo es un motor de trading en tiempo real para BTCUSDT (Binance), con cambio de temporalidades (15m, 1h, 1d, 1w). Necesito: (1) generar alertas de entrada con múltiples confirmaciones (estructura/tendencia, acción del precio, medias móviles, Fibonacci, patrones de velas) inspiradas en marcos de libros (Murphy TA, Al Brooks Price Action, Steve Nison velas, Mark Douglas psicología, Van Tharp riesgo); (2) cada trade debe tener SL/TP obligatorios y al cerrarse debe enviar una segunda alerta indicando si ganó o perdió, guardando el precio real de cierre; (3) exponer endpoints GET para ver una tabla de todas las operaciones (entrada, SL, TP, cierre, resultado, timeframe, timestamps) y un resumen por semana/mes; (4) generar gráficos locales (Plotly) donde se vean velas, zonas, SL/TP y niveles, para validar sin TradingView; (5) incluir un módulo de IA (agente con LangChain) que actúe como copiloto: journaling/post-trade review y sugerencias de mejora de reglas, considerando costos/fees de Binance por operación; (6) mantener una arquitectura por carpetas dentro de app/: config, routers, controllers, schemas, db, models, enums, services, celery_worker, middleware, util. Quiero que me entregues el código completo por archivo siguiendo esa estructura, con buenas prácticas, tipado, logging, y que sea ejecutable con docker-compose.
```

---

## 10) Próximo paso recomendado

Implementar primero un **MVP de alertas** (sin ejecutar órdenes):
1) Ingesta tiempo real (WebSocket klines).
2) Indicadores + reglas de señal.
3) Persistencia de trades OPEN y cierre WIN/LOSS.
4) API /trades + /charts/latest.
5) Alertas vía webhook/telegram.

Luego:
- backtesting (Celery/worker),
- optimización offline,
- paper trading,
- y si aplica, ejecución real con controles estrictos.

