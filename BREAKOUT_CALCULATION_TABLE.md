# 📋 TABLA DE CÁLCULO DEL BREAKOUT - TODO EN UNO

## La Ecuación Visual Paso a Paso

```
╔══════════════════════════════════════════════════════════════════╗
║              CÁLCULO DEL BREAKOUT (22:15:00 UTC)                ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  1️⃣  OBTENER HIGH MÁXIMO (de últimas 8 velas)                  ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Código: prev_high = df["high"].tail(8).max()                  ║
║                                                                  ║
║  Proceso:                                                        ║
║  Vela 293: $90,156.32  ┐                                        ║
║  Vela 294: $90,543.21  │                                        ║
║  Vela 295: $90,612.95  │ últimas 8 velas                       ║
║  Vela 296: $90,643.81  ├─→ máximo = $90,643.81                 ║
║  Vela 297: $90,287.00  │                                        ║
║  Vela 298: $90,401.12  │                                        ║
║  Vela 299: $90,398.56  │                                        ║
║  Vela 300: $90,621.10  ┘                                        ║
║                                                                  ║
║  Resultado: prev_high = $90,643.81                              ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  2️⃣  OBTENER LOW MÍNIMO (de últimas 8 velas)                   ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Código: prev_low = df["low"].tail(8).min()                    ║
║                                                                  ║
║  Proceso:                                                        ║
║  Vela 293: $90,112.45  ┐                                        ║
║  Vela 294: $90,213.87  │                                        ║
║  Vela 295: $90,287.00  │ últimas 8 velas                       ║
║  Vela 296: $90,113.87  ├─→ mínimo = $90,113.87                 ║
║  Vela 297: $90,156.32  │                                        ║
║  Vela 298: $90,201.12  │                                        ║
║  Vela 299: $90,398.56  │                                        ║
║  Vela 300: $90,300.10  ┘                                        ║
║                                                                  ║
║  Resultado: prev_low = $90,113.87                               ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  3️⃣  OBTENER PRECIO ACTUAL                                      ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Código: last_price = df["close"].iloc[-1]                     ║
║                                                                  ║
║  Vela 300 (última):                                              ║
║  ├─ open:  $90,445.23                                           ║
║  ├─ high:  $90,621.10                                           ║
║  ├─ low:   $90,300.10                                           ║
║  └─ close: $90,392.52  ← Este es el precio actual              ║
║                                                                  ║
║  Resultado: last_price = $90,392.52                             ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  4️⃣  COMPARAR PARA BREAKOUT ALCISTA                             ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Pregunta: ¿El precio ROMPIÓ HACIA ARRIBA?                     ║
║  Código:   breakout_up = last_price > prev_high                ║
║                                                                  ║
║  Evaluación:                                                     ║
║           $90,392.52 > $90,643.81?                              ║
║             Precio        Alto máx                              ║
║                                                                  ║
║           90392.52 > 90643.81?  ← Comparación numérica         ║
║                NO               ← Resultado                     ║
║                                                                  ║
║  breakout_up = False  ❌                                        ║
║                                                                  ║
║  Diferencia: Falta subir $251.29                               ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  5️⃣  COMPARAR PARA BREAKOUT BAJISTA                             ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Pregunta: ¿El precio ROMPIÓ HACIA ABAJO?                      ║
║  Código:   breakout_down = last_price < prev_low               ║
║                                                                  ║
║  Evaluación:                                                     ║
║           $90,392.52 < $90,113.87?                              ║
║             Precio        Bajo mín                              ║
║                                                                  ║
║           90392.52 < 90113.87?  ← Comparación numérica         ║
║                NO               ← Resultado                     ║
║                                                                  ║
║  breakout_down = False  ❌                                      ║
║                                                                  ║
║  Diferencia: Falta bajar $278.65                               ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  6️⃣  CALCULAR PORCENTAJE DE DIFERENCIA                          ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Para ROMPER HACIA ARRIBA:                                      ║
║  ────────────────────────                                       ║
║  diff_to_high = ((prev_high - last_price) / last_price) × 100  ║
║               = ((90643.81 - 90392.52) / 90392.52) × 100        ║
║               = (251.29 / 90392.52) × 100                       ║
║               = 0.002778 × 100                                  ║
║               = 0.2778%                                         ║
║               ≈ 0.28%                                           ║
║                                                                  ║
║  Para ROMPER HACIA ABAJO:                                       ║
║  ──────────────────────                                         ║
║  diff_to_low = ((last_price - prev_low) / last_price) × 100    ║
║              = ((90392.52 - 90113.87) / 90392.52) × 100         ║
║              = (278.65 / 90392.52) × 100                        ║
║              = 0.003083 × 100                                   ║
║              = 0.3083%                                          ║
║              ≈ 0.31%                                            ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🎯 RESULTADO FINAL                                              ║
║  ─────────────────────────────────────────────────────────────  ║
║                                                                  ║
║  Salida en Logs:                                                 ║
║  ❌ Sin breakout (falta 0.28% para high, 0.31% desde low)      ║
║                                                                  ║
║  Desglose:                                                       ║
║  ├─ breakout_up = False   ❌ (no rompe hacia arriba)           ║
║  ├─ breakout_down = False ❌ (no rompe hacia abajo)            ║
║  ├─ signal = None                                               ║
║  └─ NO ENVÍA ALERTA TELEGRAM                                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Tabla Comparativa: Qué Necesitaría Pasar

```
╔════════════════════════════════════════════════════════════════════╗
║         ESCENARIOS: QUÉ PASARÍA CON DIFERENTES PRECIOS           ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║ ESCENARIO 1: PRECIO SUBE A $90,643.82 (rompe HIGH)               ║
║ ─────────────────────────────────────────────────────────────────  ║
║ last_price = $90,643.82                                           ║
║                                                                    ║
║ breakout_up = $90,643.82 > $90,643.81?                            ║
║             = SÍ  ✅ TRUE                                         ║
║                                                                    ║
║ signal = "LONG"                                                   ║
║ entry = $90,643.82                                                ║
║ stop_loss = $90,643.82 - (1.5 × $285) = $90,216.82              ║
║ take_profit = $90,643.82 + (2 × 427) = $91,498.00               ║
║                                                                    ║
║ 📨 ENVÍA ALERTA A TELEGRAM                                         ║
║    "🚀 SEÑAL LONG | Precio: $90,643.82 | Entry | SL | TP"       ║
║                                                                    ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║ ESCENARIO 2: PRECIO BAJA A $90,113.86 (rompe LOW)                ║
║ ─────────────────────────────────────────────────────────────────  ║
║ last_price = $90,113.86                                           ║
║                                                                    ║
║ breakout_down = $90,113.86 < $90,113.87?                          ║
║               = SÍ  ✅ TRUE                                       ║
║                                                                    ║
║ signal = "SHORT"                                                  ║
║ entry = $90,113.86                                                ║
║ stop_loss = $90,113.86 + (1.5 × $285) = $90,541.86              ║
║ take_profit = $90,113.86 - (2 × 427) = $89,259.00               ║
║                                                                    ║
║ 📨 ENVÍA ALERTA A TELEGRAM                                         ║
║    "📉 SEÑAL SHORT | Precio: $90,113.86 | Entry | SL | TP"      ║
║                                                                    ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║ ESCENARIO 3: PRECIO SE QUEDA EN MEDIO ($90,392.52)               ║
║ ─────────────────────────────────────────────────────────────────  ║
║ last_price = $90,392.52 (actual ahora)                            ║
║                                                                    ║
║ breakout_up = $90,392.52 > $90,643.81?  = NO  ❌                 ║
║ breakout_down = $90,392.52 < $90,113.87? = NO  ❌                ║
║                                                                    ║
║ signal = None                                                     ║
║ entry = None                                                      ║
║ stop_loss = None                                                  ║
║ take_profit = None                                                ║
║                                                                    ║
║ 🚫 NO ENVÍA ALERTA                                                 ║
║    Sistema en espera                                              ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Resumen: La Lógica Booleana Simple

```
IF last_price > prev_high:
   breakout_up = TRUE ✅
   → ENVÍA ALERTA LONG

ELIF last_price < prev_low:
   breakout_down = TRUE ✅
   → ENVÍA ALERTA SHORT

ELSE:
   breakout = FALSE ❌
   → NO ENVÍA NADA
   → ESPERA

```

**En números (ahora):**
```
$90,392.52 > $90,643.81?  ← Pregunta 1
    NO        >    NO      ← FALSE

$90,392.52 < $90,113.87?  ← Pregunta 2
    NO        <    NO      ← FALSE

Ambas FALSE → No envía → Espera
```

---

## La Ecuación Completa en Una Línea

```
breakout = (precio_actual > high_8_velas) OR (precio_actual < low_8_velas)
breakout = ($90,392.52 > $90,643.81) OR ($90,392.52 < $90,113.87)
breakout = FALSE OR FALSE
breakout = FALSE ❌ → Sin alerta
```
