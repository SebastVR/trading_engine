# 🔴 FLUJO COMPLETO: CÓMO EL SISTEMA DECIDE ENVIAR ALERTAS

## 1️⃣ CADA 5 MINUTOS (Modo Simple)

```
⏰ 22:15:00 UTC
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Celery Beat ejecuta: monitor_market_signals_simple
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
        ┌─────────────────────────────────┐
        │ SimpleSignalController           │
        │ .get_simple_signal()             │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ Obtener datos BTCUSDT 15m       │
        │ - 300 velas de Binance          │
        └────────────┬────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────┐
        │ StrategyEngine.compute_signal()  │
        │ Analizar 4 confirmaciones        │
        └────────────┬────────────────────┘
                     │
    ┌────────────────┼────────────────────┐
    │                │                    │
    ▼                ▼                    ▼
┌──────────┐  ┌──────────┐          ┌──────────┐
│ TENDENCIA│  │ BREAKOUT │  ✓       │RSI & ATR │
│ ✅ BAJISTA │  │ ❌ NO    │  ×       │✅ OK     │
└──────────┘  └──────────┘          └──────────┘
    │                │                    │
    └────────────────┼────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ Evaluar TODAS las 4:         │
        │                              │
        │ 3 de 4 = ❌ NO VÁLIDO        │
        │ (Falta breakout)             │
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ signal_result = {             │
        │   "signal": None,    ← NULA  │
        │   "entry": None,              │
        │   "stop_loss": None,          │
        │   "take_profit": None         │
        │ }                             │
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ if signal_result["signal"]:  │
        │   (EVALUACIÓN)               │
        │   None = False               │
        │   → NO ENTRA AL IF ❌        │
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ await telegram_service       │
        │ .send_signal_alert()         │
        │   (NO SE EJECUTA)            │
        └────────────┬─────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │ RESULTADO:                   │
        │ ❌ Sin alerta Telegram       │
        │ ❌ Sin trade guardado en DB  │
        │ ✅ Retorna: price, sig=None  │
        └──────────────────────────────┘
```

---

## 2️⃣ EL PUNTO CRÍTICO: MEDICIÓN DEL BREAKOUT

```
               ┌──────────────────────────────────┐
               │ StrategyEngine.compute_signal()  │
               └──────────────┬───────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │ Obtener últimas 8 velas  │
                   └──────────────┬───────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
    ┌─────────────┐      ┌──────────────┐         ┌─────────────┐
    │ HIGH máximo │      │ Precio actual│         │ LOW mínimo  │
    │ (8 velas)   │      │ (cierre hora)│         │ (8 velas)   │
    │ $90,643.81  │      │ $90,392.52   │         │ $90,113.87  │
    └──────┬──────┘      └──────┬───────┘         └──────┬──────┘
           │                    │                       │
           │                    ▼                       │
           │            ┌────────────────────────┐     │
           │            │ breakout_up =          │     │
           │            │ precio > prev_high?    │     │
           │            │                        │     │
           │            │ $90,392.52 > $90,643.81│     │
           │            │ ❌ FALSE               │     │
           │            └────────────────────────┘     │
           │                                           │
           └───────────────────┬───────────────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │ breakout_down =          │
                    │ precio < prev_low?       │
                    │                          │
                    │ $90,392.52 < $90,113.87  │
                    │ ❌ FALSE                 │
                    └──────────────┬───────────┘
                                   │
                    ┌──────────────▼────────────┐
                    │ breakout_up = FALSE       │
                    │ breakout_down = FALSE     │
                    │                          │
                    │ ❌ SIN BREAKOUT CONFIRMADO
                    └──────────────┬────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │ signal_result =              │
                    │ {                            │
                    │  "signal": None              │
                    │ }                            │
                    └──────────────────────────────┘
```

---

## 3️⃣ POR QUÉ NO SE ENVÍA TELEGRAM

```
Archivo: app/controllers/simple_signal_controller.py
Línea: 62-70

62:  # Enviar alerta a Telegram SI HAY SEÑAL
63:  if signal_result["signal"]:  ← ¿Es None? → FALSE
64:      await self.telegram_service.send_signal_alert(
65:          symbol=self.symbol,
66:          signal_type=signal_result["signal"].value,
67:          price=response["price"],
68:          entry=signal_result.get("entry"),
69:          stop_loss=signal_result.get("stop_loss"),
70:          take_profit=signal_result.get("take_profit"),

🔴 if signal_result["signal"]:
   └─→ if None:
       └─→ False (no se ejecuta)
```

**Analógía:**
```python
# Es como decir:
if "tengo dinero":
    "compro algo"

signal_result["signal"] = None
if None:  # ← Python interpreta como False
    # NO ENTRA

# Nunca llega a:
await self.telegram_service.send_signal_alert(...)
```

---

## 4️⃣ LA MEDICIÓN EXACTA EN NÚMEROS

```
┌─────────────────────────────────────────────────────┐
│ COMPARACIÓN DE PRECIOS (22:15:00 UTC)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ $90,643.81  ← HIGH 8 VELAS                          │
│             │                                      │
│             │ Diferencia: +$251.29                │
│             │ Porcentaje: +0.278%                 │
│             │ Status: Falta para subir ❌         │
│             ▼                                      │
│ $90,392.52  ← PRECIO ACTUAL                         │
│             │                                      │
│             │ Diferencia: -$278.65                │
│             │ Porcentaje: -0.308%                 │
│             │ Status: Falta para bajar ❌         │
│             ▼                                      │
│ $90,113.87  ← LOW 8 VELAS                           │
│                                                     │
│ RANGO TOTAL: $529.94 (0.586%)                      │
│ PRECIO EN MEDIO: Sin señal                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 5️⃣ CRONOLOGÍA DE EVENTOS (22:15 - 22:30)

```
🕐 22:15:00 - CICLO 1 (15 min)
    ├─ Precio: $90,392.52
    ├─ High: $90,643.81 (falta +0.28%)
    ├─ Low: $90,113.87 (falta -0.31%)
    ├─ Evaluación: Tendencia ✅ + RSI ✅ + ATR ✅ + Breakout ❌
    ├─ Signal: None
    └─ Telegram: ❌ NO ENVIADO

🕐 22:20:00 - CICLO 2 (5 min)
    ├─ Precio: $90,533.28
    ├─ High: $90,643.81 (falta +0.12%)
    ├─ Low: $90,113.87 (falta -0.46%)
    ├─ Evaluación: Tendencia ✅ + RSI ✅ + ATR ✅ + Breakout ❌
    ├─ Signal: None
    └─ Telegram: ❌ NO ENVIADO

🕐 22:25:00 - CICLO 3 (15 min)
    ├─ Precio: $90,447.37
    ├─ High: $90,643.81 (falta +0.22%)
    ├─ Low: $90,113.87 (falta -0.37%)
    ├─ Evaluación: Tendencia ✅ + RSI ✅ + ATR ✅ + Breakout ❌
    ├─ Signal: None
    └─ Telegram: ❌ NO ENVIADO

⏳ ESPERANDO: Precio > $90,643.81 o < $90,113.87
```

---

## 🎯 RESPUESTA DIRECTA A TU PREGUNTA

**"¿Por qué el sistema no está enviando alertas?"**

### 1. Medición del Breakout:
```python
prev_high = float(df["high"].tail(8).max())  # $90,643.81
last_price = float(df["close"].iloc[-1])     # $90,392.52
breakout_up = last_price > prev_high         # False ❌
```

### 2. Decisión de Señal:
```python
if trend_up and breakout_up and rsi_ok_long and last_atr > 0:
   # ✅ ✅ ✅ ❌ ← Falla
   return signal  # NO SE EJECUTA
else:
   return None  # ← Retorna esto
```

### 3. Envío de Alerta:
```python
if signal_result["signal"]:  # if None:
   await telegram_service.send_signal_alert(...)  # NO ENTRA
else:
   # Silenciosamente, sin alerta
```

---

## ✅ SÍNTESIS

| Paso | Evaluación | Resultado |
|------|------------|-----------|
| Medir HIGH 8 velas | $90,643.81 | ✅ Obtenido |
| Medir precio actual | $90,392.52 | ✅ Obtenido |
| Comparar: precio > high? | $90,392.52 > $90,643.81 | ❌ FALSE |
| Comparar: precio < low? | $90,392.52 < $90,113.87 | ❌ FALSE |
| Signal válida? | 3 de 4 filtros | ❌ NO |
| Signal result | None | ❌ NULA |
| ¿Enviar alerta? | if None | ❌ FALSE |
| **Resultado final** | **NO HAY ALERTA** | **❌ NO ENVIADO** |

**El sistema funciona perfectamente. Espera que el precio rompa un nivel.** 🚀
