# 🔢 CÁLCULO EXACTO DEL BREAKOUT - DESGLOSADO PASO A PASO

## 🎯 EL BREAKOUT EN 3 LÍNEAS DE CÓDIGO

```python
# Línea 1: Obtener HIGH máximo de últimas N velas
prev_high = float(df["high"].tail(lookback).max())

# Línea 2: Obtener precio actual (cierre)
last_price = float(df["close"].iloc[-1])

# Línea 3: Comparar
breakout_up = last_price > prev_high    # ¿Precio rompe hacia arriba?
breakout_down = last_price < prev_low   # ¿Precio rompe hacia abajo?
```

---

## 📊 PASO 1: OBTENER LAS ÚLTIMAS N VELAS

### **Código:**
```python
lookback = 8  # (o 5 si ATR > 500)

prev_high = float(df["high"].tail(lookback).max())
```

### **¿Qué significa?**

```
df = DataFrame de 300 velas de Binance
     ↓
df["high"] = todas las alturas
     ↓
.tail(8) = últimas 8 velas
     ↓
.max() = altura MÁXIMA de esas 8
     ↓
float() = convertir a número
```

### **Ejemplo Real (22:15:00 UTC):**

```
Vela 293: high = $90,156.32
Vela 294: high = $90,543.21
Vela 295: high = $90,612.95
Vela 296: high = $90,643.81  ← MAX (el más alto)
Vela 297: high = $90,287.00
Vela 298: high = $90,401.12
Vela 299: high = $90,398.56
Vela 300: high = $90,621.10

.tail(8).max() = $90,643.81
```

---

## 📊 PASO 2: OBTENER EL LOW MÍNIMO

### **Código:**
```python
prev_low = float(df["low"].tail(lookback).min())
```

### **Ejemplo Real:**

```
Vela 293: low = $90,112.45
Vela 294: low = $90,213.87
Vela 295: low = $90,287.00
Vela 296: low = $90,113.87  ← MIN (el más bajo)
Vela 297: low = $90,156.32
Vela 298: low = $90,201.12
Vela 299: low = $90,398.56
Vela 300: low = $90,300.10

.tail(8).min() = $90,113.87
```

---

## 💰 PASO 3: OBTENER PRECIO ACTUAL

### **Código:**
```python
last_price = float(df["close"].iloc[-1])
```

### **¿Qué significa?**

```
df["close"] = todos los cierres
     ↓
.iloc[-1] = el ÚLTIMO (posición -1)
     ↓
float() = convertir a número decimal
```

### **Ejemplo Real:**

```
Última vela (300):
├─ open:  $90,445.23
├─ high:  $90,621.10
├─ low:   $90,300.10
└─ close: $90,392.52  ← last_price

last_price = $90,392.52
```

---

## ✅ PASO 4: COMPARACIÓN DEL BREAKOUT

### **Código:**
```python
breakout_up = last_price > prev_high
breakout_down = last_price < prev_low
```

### **Para LONG (Alcista):**

```
Pregunta: ¿last_price > prev_high?
          $90,392.52 > $90,643.81?
          
Respuesta: NO → False
          
breakout_up = False  ❌
```

### **Para SHORT (Bajista):**

```
Pregunta: ¿last_price < prev_low?
          $90,392.52 < $90,113.87?
          
Respuesta: NO → False
          
breakout_down = False  ❌
```

---

## 🔴 PASO 5: MOSTRAR EN LOGS

### **Código (líneas 115-117):**

```python
else:
    diff_to_high = ((prev_high - last_price) / last_price) * 100
    diff_to_low = ((last_price - prev_low) / last_price) * 100
    print(f"❌ Sin breakout (falta {diff_to_high:.2f}% para high, {diff_to_low:.2f}% desde low)")
```

### **Cálculo de diferencia para LONG (hacia arriba):**

```
diff_to_high = ((prev_high - last_price) / last_price) * 100
             = (($90,643.81 - $90,392.52) / $90,392.52) * 100
             = ($251.29 / $90,392.52) * 100
             = 0.002778 * 100
             = 0.2778%
             = 0.28% (redondeado)
             
Log: "falta 0.28% para high"
```

### **Cálculo de diferencia para SHORT (hacia abajo):**

```
diff_to_low = ((last_price - prev_low) / last_price) * 100
            = (($90,392.52 - $90,113.87) / $90,392.52) * 100
            = ($278.65 / $90,392.52) * 100
            = 0.003083 * 100
            = 0.3083%
            = 0.31% (redondeado)
            
Log: "0.31% desde low"
```

---

## 📈 TABLA DE CÁLCULO COMPLETA

| Operación | Fórmula | Valor |
|-----------|---------|-------|
| **1. High máximo** | `df["high"].tail(8).max()` | $90,643.81 |
| **2. Low mínimo** | `df["low"].tail(8).min()` | $90,113.87 |
| **3. Precio actual** | `df["close"].iloc[-1]` | $90,392.52 |
| **4. Break UP?** | `$90,392.52 > $90,643.81?` | ❌ FALSE |
| **5. Break DOWN?** | `$90,392.52 < $90,113.87?` | ❌ FALSE |
| **6. Falta para up** | `(251.29 / 90,392.52) × 100` | 0.28% |
| **7. Falta para down** | `(278.65 / 90,392.52) × 100` | 0.31% |

---

## 🎨 VISUALIZACIÓN GRÁFICA DEL CÁLCULO

```
                HIGH MÁXIMO
                    ↓
            $90,643.81 ──────────── ← prev_high
                        ╱│╲
                       ╱ │ ╲
                      ╱  │  ╲
                     ╱   │   ╲
                    ╱    │    ╲
$90,392.52 ──────→ ├─────│─────┤ ← last_price (SIN ROMPER)
                    ╲    │    ╱
                     ╲   │   ╱
                      ╲  │  ╱
                       ╲ │ ╱
            $90,113.87 ──────────── ← prev_low
                        ↑
                 LOW MÍNIMO

RESULTADO:
┌─────────────────────────────────────┐
│ Precio NO rompe HIGH ($90,643.81)   │
│ Precio NO rompe LOW ($90,113.87)    │
│ breakout_up = FALSE                 │
│ breakout_down = FALSE               │
└─────────────────────────────────────┘
```

---

## 🔍 DESGLOSE DE VARIABLES

### **¿De dónde viene cada valor?**

```
df (DataFrame)
├─ 300 velas de BTCUSDT en timeframe 15m
├─ Columnas: open, high, low, close, volume
└─ Descargadas de Binance API

df["high"].tail(8)
├─ Selecciona columna "high"
├─ Toma últimas 8 filas
└─ Resultado: [90156.32, 90543.21, 90612.95, 90643.81, 90287.00, 90401.12, 90398.56, 90621.10]

.max()
├─ Busca el máximo de esa lista
└─ Resultado: 90643.81

df["low"].tail(8).min()
├─ Selecciona columna "low"
├─ Toma últimas 8 filas
├─ Busca el mínimo
└─ Resultado: 90113.87

df["close"].iloc[-1]
├─ Selecciona columna "close"
├─ Toma la última fila (-1 = último)
└─ Resultado: 90392.52
```

---

## 💻 CÓDIGO COMPLETO DEL CÁLCULO

```python
# ════════════════════════════════════════════════════
# PASO 1: DEFINIR LOOKBACK (8 o 5 según ATR)
# ════════════════════════════════════════════════════
base_lookback = 8
if last_atr > 500:
    lookback = 5
else:
    lookback = base_lookback
# Resultado: lookback = 8


# ════════════════════════════════════════════════════
# PASO 2: OBTENER HIGH/LOW DE LAS ÚLTIMAS N VELAS
# ════════════════════════════════════════════════════
prev_high = float(df["high"].tail(lookback).max())
# → $90,643.81

prev_low = float(df["low"].tail(lookback).min())
# → $90,113.87


# ════════════════════════════════════════════════════
# PASO 3: OBTENER PRECIO ACTUAL
# ════════════════════════════════════════════════════
last_price = float(df["close"].iloc[-1])
# → $90,392.52


# ════════════════════════════════════════════════════
# PASO 4: COMPARAR PARA DETECTAR BREAKOUT
# ════════════════════════════════════════════════════
breakout_up = last_price > prev_high
# → $90,392.52 > $90,643.81?
# → False ❌

breakout_down = last_price < prev_low
# → $90,392.52 < $90,113.87?
# → False ❌


# ════════════════════════════════════════════════════
# PASO 5: CALCULAR DISTANCIA SI NO HAY BREAKOUT
# ════════════════════════════════════════════════════
diff_to_high = ((prev_high - last_price) / last_price) * 100
# = (($90,643.81 - $90,392.52) / $90,392.52) * 100
# = 0.2778%

diff_to_low = ((last_price - prev_low) / last_price) * 100
# = (($90,392.52 - $90,113.87) / $90,392.52) * 100
# = 0.3083%


# ════════════════════════════════════════════════════
# PASO 6: MOSTRAR EN LOGS
# ════════════════════════════════════════════════════
if breakout_up:
    print("✅ BREAKOUT ALCISTA (precio > high previo)")
elif breakout_down:
    print("✅ BREAKOUT BAJISTA (precio < low previo)")
else:
    print(f"❌ Sin breakout (falta {diff_to_high:.2f}% para high, {diff_to_low:.2f}% desde low)")

# Output:
# ❌ Sin breakout (falta 0.28% para high, 0.31% desde low)
```

---

## 🎯 RESUMEN: CÓMO SE CALCULA EL BREAKOUT

| Paso | Operación | Resultado |
|------|-----------|-----------|
| 1️⃣ | `df["high"].tail(8).max()` | High = $90,643.81 |
| 2️⃣ | `df["low"].tail(8).min()` | Low = $90,113.87 |
| 3️⃣ | `df["close"].iloc[-1]` | Precio = $90,392.52 |
| 4️⃣ | `$90,392.52 > $90,643.81?` | breakout_up = False ❌ |
| 5️⃣ | `$90,392.52 < $90,113.87?` | breakout_down = False ❌ |
| 6️⃣ | `(251.29 / 90,392.52) × 100` | Falta 0.28% para subir |
| 7️⃣ | `(278.65 / 90,392.52) × 100` | Falta 0.31% para bajar |

**Resultado Final:** ❌ **Sin breakout confirmado**
