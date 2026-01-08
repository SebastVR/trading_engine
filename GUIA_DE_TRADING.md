# 🎯 GUÍA DE TRADING: Cómo Operar con las Señales del Sistema

## 📊 INTERPRETACIÓN DE SEÑALES

### ❌ **SIN SEÑAL** (`signal: null`)
```json
{
  "signal": null,
  "reason": {"note": "No setup con confirmaciones suficientes"}
}
```

**🚫 NO OPERAR**
- El mercado no cumple todos los requisitos
- Esperar confirmación
- Monitorear hasta que aparezca señal clara

---

### 🟢 **SEÑAL LONG** - COMPRAR BTC

#### Ejemplo de Señal:
```json
{
  "symbol": "BTCUSDT",
  "signal": "LONG",
  "now_price": 91000.00,
  "entry": 91000.00,
  "stop_loss": 89463.92,
  "take_profit": 94072.16
}
```

#### ✅ Qué hacer en BINANCE:

**Paso 1: COMPRAR (Entry)**
```
1. Abre Binance → Spot Trading
2. Busca BTC/USDT
3. Click en COMPRAR (verde)
4. Tipo: Market Order
5. Cantidad: $100, $500, $1000 (según tu capital)
6. Confirmar
```

**Paso 2: PROTEGER (Stop Loss & Take Profit)**
```
1. Ve a Órdenes → Crear OCO Order
2. Stop-Limit:
   - Precio Stop: $89,463.92
   - Precio Limit: $89,400.00 (un poco más bajo)
3. Limit (Take Profit):
   - Precio: $94,072.16
4. Confirmar
```

#### 💰 Cálculo de Riesgo:
```
Inversión: $1,000
Entry: $91,000
Stop Loss: $89,463.92 (-1.69%)
Take Profit: $94,072.16 (+3.38%)

Si toca Stop Loss: Pierdes $16.90
Si toca Take Profit: Ganas $33.80
Ratio R:R = 1:2 (arriesgas $1 para ganar $2)
```

---

### 🔴 **SEÑAL SHORT** - VENDER BTC

#### Ejemplo de Señal:
```json
{
  "symbol": "BTCUSDT",
  "signal": "SHORT",
  "now_price": 91000.00,
  "entry": 91000.00,
  "stop_loss": 92536.08,
  "take_profit": 87927.84
}
```

#### ✅ Qué hacer en BINANCE:

**Opción A: SPOT (Si ya tienes BTC)**
```
1. Ve a Spot Trading
2. Busca BTC/USDT
3. Click en VENDER (rojo)
4. Vende tu BTC a USDT
5. Espera que baje
6. Recompra cuando toque Take Profit
```

**Opción B: FUTURES (Más avanzado)**
```
1. Abre Binance Futures
2. Busca BTCUSDT Perpetual
3. Click en VENDER/SHORT (rojo)
4. Apalancamiento: 1x-3x (principiantes)
5. Cantidad: Según tu capital
6. Stop Loss: $92,536.08
7. Take Profit: $87,927.84
8. Confirmar
```

⚠️ **ADVERTENCIA FUTURES:**
- Apalancamiento multiplica riesgo
- Puedes perder más de tu inversión inicial
- Solo para traders con experiencia
- Practica primero en TESTNET

---

## 🎯 CONSENSO MULTI-TIMEFRAME (RECOMENDADO)

### ¿Por qué es mejor?
- ✅ Analiza 4 timeframes: 15m, 1h, 4h, 1d
- ✅ Requiere confirmación en ≥2 timeframes
- ✅ Mayor confianza = Mayor probabilidad de éxito
- ✅ Recibe alerta automática en Telegram

### Ejemplo de Consenso FUERTE:

```json
{
  "consensus": {
    "signal": "LONG",
    "confidence": 80.0,
    "weighted_score": +45.5
  },
  "votes": {
    "long": 3,
    "short": 0,
    "neutral": 1
  },
  "trading_setup": {
    "entry_price": 91000.00,
    "stop_loss": 89463.92,
    "take_profit": 94072.16,
    "risk_reward_ratio": 2.0,
    "based_on_timeframe": "1d"
  }
}
```

#### 🟢 Señales de Alta Confianza:
- **80-100%**: 🔥 FUERTE - Alta probabilidad
- **70-79%**: 🟢 BUENA - Probabilidad moderada-alta
- **50-69%**: 🟡 MODERADA - Considerar con precaución
- **0-49%**: ⚪ DÉBIL - Esperar mejor oportunidad

---

## 📱 CONFIGURACIÓN DE ALERTAS

### Telegram (Ya configurado ✅)
Recibirás mensajes automáticamente cuando:
- Haya consenso entre ≥2 timeframes
- Confianza ≥50%

**Ejemplo de alerta:**
```
🟢 CONSENSO MULTI-TIMEFRAME 🟢

Par: BTCUSDT
Decisión: COMPRAR
Confianza: 80.0%
Score Ponderado: +45.5

📊 Votos por Timeframe:
  • LONG: 3
  • SHORT: 0
  • NEUTRAL: 1

Precio Actual: $91,000.00

💰 Setup Recomendado:
  • Entry: $91,000.00
  • Stop Loss: $89,463.92 (-1.69%)
  • Take Profit: $94,072.16 (+3.38%)
  • R:R = 1:2.00
```

---

## ⚙️ MONITOREO EN TIEMPO REAL

### Opción 1: Manual (cada 5 minutos)
```bash
watch -n 300 'curl -s http://localhost:85/trades/multi-signal'
```

### Opción 2: Ver logs del sistema
```bash
docker logs -f trading_engine_api
```

### Opción 3: Telegram (RECOMENDADO)
- Automático
- Sin necesidad de estar en la computadora
- Alertas instantáneas

---

## 🎓 ESTRATEGIA DE CONFIRMACIONES

El sistema requiere **4 confirmaciones** para emitir señal:

### Para LONG (Comprar):
1. ✅ **Tendencia ALCISTA**: MA rápida > MA lenta
2. ✅ **Breakout ALCISTA**: Precio rompe máximo de últimas 20 velas
3. ✅ **RSI**: Entre 45-70 (no sobrecomprado)
4. ✅ **ATR**: Válido para calcular Stop Loss

### Para SHORT (Vender):
1. ✅ **Tendencia BAJISTA**: MA rápida < MA lenta
2. ✅ **Breakout BAJISTA**: Precio rompe mínimo de últimas 20 velas
3. ✅ **RSI**: Entre 30-55 (no sobrevendido)
4. ✅ **ATR**: Válido para calcular Stop Loss

**Si falta 1 confirmación → NO hay señal**

---

## 💡 MEJORES PRÁCTICAS

### ✅ HACER:
1. **Esperar consenso**: 2+ timeframes coincidiendo
2. **Usar Stop Loss**: SIEMPRE protege tu capital
3. **Respetar R:R**: Solo operar si R:R ≥ 1.5:1
4. **Risk Management**: No arriesgar >2% del capital por trade
5. **Seguir el plan**: No modificar SL/TP por emociones
6. **Testear primero**: Usa Binance Testnet antes de real

### ❌ NO HACER:
1. **Operar sin señal**: Esperar confirmación del sistema
2. **Ignorar Stop Loss**: Es tu seguro de vida
3. **Over-trading**: No operar por aburrimiento
4. **FOMO**: No entrar si ya subió mucho después de la señal
5. **Apalancamiento alto**: Máximo 3x para principiantes
6. **Mover Stop Loss**: Mantenlo fijo después de colocar

---

## 🧮 CALCULADORA DE POSICIÓN

### Ejemplo con $1,000 de capital:

**Regla: No arriesgar más de 2% por trade**

```
Capital: $1,000
Riesgo máximo: 2% = $20

Ejemplo de señal LONG:
Entry: $91,000
Stop Loss: $89,463.92
Diferencia: $1,536.08 (1.69%)

Tamaño de posición:
$20 / $1,536.08 = 0.013 BTC
= $1,183 USDT

⚠️ En este caso, el riesgo es bajo (1.69%)
Puedes usar $1,000 completos si quieres
```

---

## 🔄 EJEMPLO COMPLETO DE OPERACIÓN

### 1. Recibes Alerta en Telegram:
```
🟢 CONSENSO MULTI-TIMEFRAME 🟢
Par: BTCUSDT
Decisión: COMPRAR
Confianza: 75.5%
Entry: $91,000.00
Stop Loss: $89,463.92
Take Profit: $94,072.16
R:R = 1:2.00
```

### 2. Verificas en el sistema:
```bash
curl http://localhost:85/trades/multi-signal
```

### 3. Abres Binance:
- Vas a Spot Trading → BTC/USDT
- Compras $1,000 de BTC (~0.011 BTC)
- Precio de compra: $91,000

### 4. Configuras protecciones:
- OCO Order:
  - Stop Loss: $89,463.92
  - Take Profit: $94,072.16

### 5. Resultados posibles:

**Escenario A: Toca Take Profit** 🎉
```
Compra: $91,000
Venta: $94,072.16
Ganancia: $3,072.16 = +3.38%
En $1,000 invertidos: $33.80 de ganancia
```

**Escenario B: Toca Stop Loss** 😐
```
Compra: $91,000
Venta: $89,463.92
Pérdida: -$1,536.08 = -1.69%
En $1,000 invertidos: -$16.90 de pérdida
```

### 6. Estadísticas (si haces 10 trades):
```
Wins: 6 trades (60% winrate)
Losses: 4 trades

Ganancias: 6 × $33.80 = $202.80
Pérdidas: 4 × $16.90 = $67.60

TOTAL: $202.80 - $67.60 = +$135.20 (+13.52%)
```

---

## 📞 ENDPOINTS ÚTILES

```bash
# 1. Señal individual (timeframe actual: 4h)
curl http://localhost:85/trades/signal

# 2. Consenso multi-timeframe (RECOMENDADO)
curl http://localhost:85/trades/multi-signal

# 3. Probar Telegram
curl http://localhost:85/test/telegram

# 4. Enviar alerta de prueba
curl -X POST http://localhost:85/test/telegram/signal

# 5. Ver documentación
http://localhost:85/docs
```

---

## 🎯 RESUMEN EJECUTIVO

### ¿Cuándo operar?
**✅ Cuando veas esto:**
```json
{
  "consensus": {
    "signal": "LONG",  // o "SHORT"
    "confidence": 75.5  // ≥50%
  }
}
```

### ¿Cómo operar?
1. Abre Binance
2. Compra/Vende según la señal
3. Coloca Stop Loss y Take Profit
4. Espera pacientemente

### ¿Qué esperar?
- Winrate: 50-70% (si la estrategia es buena)
- R:R: 1:2 (arriesgas $1 para ganar $2)
- Rentabilidad: 10-30% mensual (si todo va bien)

---

⚠️ **DISCLAIMER**:
- Trading tiene riesgos, puedes perder dinero
- Este sistema es una herramienta, no una garantía
- Practica primero en cuenta demo
- No inviertas más de lo que puedes perder
- La rentabilidad pasada no garantiza resultados futuros

---

✅ **Sistema configurado y listo para operar**
📱 Recibirás alertas automáticas en Telegram
🎯 Espera señales con alta confianza (≥70%)
💰 Sigue el plan y gestiona el riesgo
