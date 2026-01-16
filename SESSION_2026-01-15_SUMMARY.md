# Trading Engine — Resumen de sesión (2026-01-15)

> Objetivo principal de hoy: **reducir pérdidas** haciendo que el “IA Filter” (AWS Bedrock) influya de verdad en qué señales se dejan pasar, y dejar todo **medible** (Telegram + BD) para poder ajustar con datos.

## ✅ Lo que quedó funcionando hoy

### 1) IA Filter conectado al flujo real de señales
- Se integró el análisis con AWS Bedrock (`openai.gpt-oss-120b-1:0`, región `us-east-1`).
- La IA retorna y se usa:
  - `ai_quality_score` (0–100)
  - `ai_recommendation` (`OPEN` / `WAIT` / `SKIP`)
  - `ai_reasoning`/nota (explicación corta)

### 2) Telegram ahora muestra la recomendación de la IA
- Las alertas ya incluyen un bloque final con el resultado del filtro IA:
  - recomendación
  - score
  - nota/resumen

**Valor:** permite ver en tiempo real si la IA está siendo estricta o permisiva sin entrar a la BD.

### 3) Persistencia en Base de Datos (Postgres)
- Se añadieron columnas para guardar IA en `public.trades`:
  - `ai_quality_score` (integer)
  - `ai_recommendation` (varchar)
- Ahora los trades nuevos ya guardan esas columnas (verificado consultando filas recientes).

**Valor:** habilita medición real (win/loss por score/reco, por side, por horario).

### 4) Safeguards controlables por `.env`
Quedaron disponibles (y verificados en runtime) los siguientes controles:
- `AI_FILTER_ENFORCE=True` → hace que el filtro IA “mande” (dependiendo de la lógica actual).
- `DISABLE_SHORTS=True` → bloquea señales SHORT.
- `SIGNAL_ALLOWED_HOURS_CO=...` (opcional) → filtra señales por horario Colombia (ej: `7-20`).
- `AI_QUALITY_THRESHOLD=55` → umbral actual del score.

**Detalle importante:** aunque estos toggles se configuran en `.env`, **en este commit NO se incluye el `.env`** (por seguridad). La idea es versionar el código y mantener secretos fuera del repo.

### 5) Fix operativo importante: env_file y recreación de contenedores
- Se detectó que **reiniciar** servicios no siempre refresca variables del `env_file`.
- Para aplicar cambios de `.env` se requirió **recrear** contenedores.

## 🧩 Cambios por archivo (lo que va en el commit)

### `app/config/settings.py`
- Se añadieron settings para habilitar safeguards por configuración:
  - `AI_FILTER_ENFORCE` (enforcement del filtro IA)
  - `DISABLE_SHORTS` (bloqueo de shorts)
  - `SIGNAL_ALLOWED_HOURS_CO` (ventana horaria en Colombia)

### `app/controllers/simple_signal_controller.py`
- Se conectó el endpoint/flujo de señal simple con el **IA Filter** (Bedrock):
  - se construye un payload compatible (`signal`, `entry`, `stop_loss`, `take_profit`, `confirmations`)
  - se llama a `validate_signal_quality(...)`
  - se adjunta al resultado: `ai_note`, `ai_quality_score`, `ai_recommendation`
- Se añadieron guardrails configurables:
  - filtro por hora Colombia
  - bloqueo de shorts
  - enforcement IA (bloquea si no cumple OPEN/threshold)
- Se ajustó la persistencia:
  - `ai_note` se reserva para la nota de la IA
  - el reason técnico queda en `confirmations_json`

### `app/controllers/trade_controller.py`
- Se propagan `ai_quality_score` y `ai_recommendation` hacia el trade al momento de crear.

### `app/models/trade_model.py`
- Se agregaron campos ORM para persistir IA:
  - `ai_quality_score` (int)
  - `ai_recommendation` (string)

### `app/services/telegram_service.py`
- La alerta Telegram ahora soporta y muestra:
  - recomendación IA
  - score IA
  - nota IA (truncada para no exceder longitud)

### `app/services/trade_manager.py`
- El repositorio de trades ahora acepta y guarda:
  - `ai_quality_score`
  - `ai_recommendation`

## 🛠️ Hotfixes de estabilidad (post-commit)

Después del push se aplicaron ajustes adicionales para dejar el sistema **estable para monitoreo 48h**:

### `app/controllers/simple_signal_controller.py`
- Se hizo el filtro de shorts **más robusto**:
  - en vez de depender del enum interno, se normaliza `signal_value = (response["signal"] or "").upper()`
  - con `DISABLE_SHORTS=True`, si `signal_value == "SHORT"` se devuelve:
    - `filtered: true`
    - `filtered_reason: "shorts_disabled"`
- Se hardened el flujo de IA:
  - si la llamada al IA Filter falla (por ejemplo, parseo/JSON inválido), el endpoint **no retorna 500**
  - se degrada a una validación tipo `WAIT` con `ai_error` en la nota
- Se movió el enforcement IA a una etapa más temprana para que el endpoint pueda devolver `filtered=true` de forma consistente cuando aplique.

### `app/services/trade_manager.py`
- Se agregó un guard clause al parseo de `confirmations_json` para evitar `JSONDecodeError` cuando viene vacío/dañado:
  - si falla el parseo → `confirmations = {}`
  - esto reduce el ruido tipo `Expecting value: line 1 column 1 (char 0)`

### Estado de monitoreo
- Se validó en runtime que los filtros responden y que el endpoint puede devolver respuestas filtradas.
- Queda pendiente seguir mitigando el origen exacto del `Expecting value...` en rutas multi-timeframe, pero ya no debería tumbar el sistema.

## 🧪 Verificaciones hechas hoy

- Los contenedores se levantaron con `docker compose up --build`.
- Se validó que en runtime:
  - `AI_QUALITY_THRESHOLD` quedó en `55`.
  - `DISABLE_SHORTS=True` y efectivamente filtra señales SHORT.
- Se verificó en BD que los trades recientes ya incluyen `ai_quality_score` y `ai_recommendation`.

## 📌 Configuración actual (resumen)
Archivo: `.env`
- `AI_QUALITY_THRESHOLD=55`
- `DISABLE_SHORTS=True`
- `AI_FILTER_ENFORCE=True`
- Horario Colombia: comentado (opcional)

## 🔎 Recomendaciones próximas (para bajar pérdidas con evidencia)

### A) “No shorts” → pasar a “shorts solo con IA muy alta” (recomendado)
En vez de bloquear todos los SHORT, suele funcionar mejor:
- LONG: threshold más flexible (ej. 55–65)
- SHORT: threshold más estricto (ej. 70–80) y/o solo si `ai_recommendation == OPEN`

**Motivo:** los shorts tienden a tener squeezes y movimientos violentos; si se operan, que sea con más filtro.

### B) Enforce por recomendación (no solo por score)
Política común que mejora calidad:
- `OPEN` → pasa
- `WAIT` → bloquear o permitir solo si score >= (threshold + 10)
- `SKIP` → bloquear siempre

### C) Activar horario Colombia como “modo seguro” por 24–48h
Probar:
- `SIGNAL_ALLOWED_HOURS_CO=7-17`

**Motivo:** reduce trades en ventanas con más ruido/spreads/latigazos.

### D) Medición por buckets (lo más importante)
Cuando ya haya suficientes trades nuevos con IA persistida:
- Winrate / lossrate por `ai_recommendation`
- Winrate por rangos de score (0–39, 40–54, 55–69, 70–84, 85–100)
- Separado por `side` (LONG/SHORT)

**Meta:** ajustar thresholds con datos, no intuición.

### E) Reducir el “ruido” del error JSON (`Expecting value...`)
Hay un error repetido que parece venir de parseo JSON vacío/invalid.
Recomendación:
- agregar guard clause cuando input está vacío
- loggear contexto mínimo (qué campo venía vacío) y rate-limit del mismo error

**Motivo:** evita ocultar errores reales y facilita diagnóstico.

## 🕵️ Plan de observación (próximos 2 días)

- Mantener el stack arriba.
- Mantener logs en vivo (API + Celery) para:
  - ver distribución de recomendaciones IA (OPEN/WAIT/SKIP)
  - confirmar que los filtros se aplican como esperas
  - detectar si hay un sesgo (muchos WAIT o muchos SKIP)

### Qué esperamos ver
- Menos señales ejecutables (porque hay filtros) pero mejor calidad.
- En BD: `ai_quality_score` y `ai_recommendation` siempre presentes en trades nuevos.

## ✅ Estado final
- Sistema levantado y listo para monitoreo.
- Persistencia IA lista para análisis.
- Safeguards togglables vía `.env`.

---

Si quieres, mañana armamos 2 consultas SQL “de cabecera” para:
1) conteo por recomendación + score bucket
2) win/loss por bucket y side
