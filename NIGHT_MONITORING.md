# 🌙 NOCHE DE MONITOREO - Trading Engine

**Fecha**: 2026-01-09  
**Hora de Inicio**: 04:11 UTC  
**Sistema**: Modo Experimento (Feature Branch: feature/single-timeframe)

---

## 📊 Configuración Activa

### Sistema Multi-Timeframe (Principal)
- **Timeframes**: 15m (peso 1) + 1h (peso 2) + 4h (peso 3) + 1d (peso 4)
- **Frecuencia**: Cada 15 minutos
- **Requisito**: ≥40% consenso (2 de 4 timeframes)
- **Alertas**: Telegram automático si hay señal

### Sistema Simple (Experimental)
- **Timeframe**: Solo 15m
- **Frecuencia**: Cada 5 minutos
- **Requisito**: Solo análisis técnico (sin consenso)
- **Propósito**: Comparar cantidad de señales vs multi-timeframe

---

## 🎯 Indicadores Técnicos

### Moving Averages (Tendencia)
- **MA Fast**: 10 períodos
- **MA Slow**: 30 períodos
- **Lógica**: MA Fast > MA Slow → LONG, MA Fast < MA Slow → SHORT

### RSI (Momentum)
- **Período**: 14
- **LONG**: RSI entre 40-75
- **SHORT**: RSI entre 25-60

### Breakout (Confirmación)
- **Período**: 15 velas
- **Criterio**: Cierre por encima/debajo del high/low reciente

### ATR (Stop Loss)
- **Período**: 14
- **Multiplicador SL**: 1.5x ATR
- **Multiplicador TP**: 2x Risk (R:R = 1:2)

---

## 🔔 Alertas Configuradas

### Telegram Bot
- **Token**: Configurado ✅
- **Chat ID**: Configurado ✅
- **Formato**: HTML con emojis
- **Contenido**: Señal, precio, entry, SL, TP, R:R

### Test de Alerta
- **Ejecutado**: 04:11 UTC
- **Resultado**: ✅ Éxito
- **Mensaje**: Debería haber llegado a Telegram

---

## 📈 Estado del Mercado (Último Check)

```
Par: BTCUSDT
Precio: ~$91,192.22
Tendencia 15m: BAJISTA (MA Fast < MA Slow)
RSI 15m: 51.33 (neutral)
Breakout: NO (falta 0.48% para high)

Consenso Multi-Timeframe: NINGUNO (0%)
Señal Simple 15m: NINGUNO
```

**Análisis**: Mercado lateral, sin ruptura clara. Esperando movimiento.

---

## 🚀 Tareas Automáticas Ejecutándose

### Celery Beat Schedule
| Tarea | Frecuencia | Última Ejecución | Estado |
|-------|-----------|------------------|--------|
| `monitor_market_signals` | Cada 15 min | 04:11 UTC | ✅ Activa |
| `monitor_market_signals_simple` | Cada 5 min | 04:11 UTC | ✅ Activa |

### Logs
- **Ubicación**: `/tmp/trading_logs_night.txt`
- **Streaming**: En vivo a background
- **Filtros**: Todos los eventos registrados

---

## 📋 Qué Esperamos Esta Noche

### Escenario 1: Mercado Sigue Lateral
✅ **Esperado**: Pocas o ninguna señal
- Indica que la estrategia es selectiva (correcto)
- Evita falsos positivos

### Escenario 2: Breakout al Alza
🟢 **Esperado**: LONG en 2+ timeframes
- Todos los MA deberían cruzar
- RSI debería subir
- Telegram: Alerta LONG

### Escenario 3: Breakout a la Baja
🔴 **Esperado**: SHORT en 2+ timeframes
- Todos los MA deberían cruzar
- RSI debería bajar
- Telegram: Alerta SHORT

### Escenario 4: Falso Breakout
⚪ **Esperado**: Pocas señales en 15m, pero sin consenso multi-tf
- Indica que multi-timeframe filtra ruido (correcto)

---

## 🔍 Cómo Monitorear

### En Vivo
```bash
# Ver logs en tiempo real
tail -f /tmp/trading_logs_night.txt

# Buscar señales
grep -i "SEÑAL\|LONG\|SHORT" /tmp/trading_logs_night.txt

# Contar eventos
wc -l /tmp/trading_logs_night.txt
```

### Telegram
- Recibirás notificaciones **automáticas** cuando haya señal ✅
- No necesitas hacer nada más
- Sistema está **100% automatizado**

---

## 📝 Endpoints Disponibles (Para Debug)

```bash
# Obtener estado multi-timeframe
curl http://localhost:85/trades/multi-signal

# Obtener estado simple 15m
curl http://localhost:85/trades/simple-signal

# Health check
curl http://localhost:85/health
```

---

## 🎯 Resumen

✅ **Sistema Activo**: 5 contenedores corriendo  
✅ **Telegram**: Probado y funcionando  
✅ **Celery Beat**: Monitoreando cada 5-15 minutos  
✅ **Logs**: Grabándose en `/tmp/trading_logs_night.txt`  
✅ **Alertas**: Automáticas a Telegram  

**Tu trabajo**: Esperar y revisar Telegram si hay alertas 📱

---

## 🔮 Mañana

1. Revisar logs en `/tmp/trading_logs_night.txt`
2. Contar cuántas señales se generaron
3. Comparar Multi-Timeframe vs Simple
4. Decidir: ¿Mantener Multi? ¿Cambiar a Simple? ¿Híbrido?

---

**Sistema listo para monitoreo nocturno** 🌙🤖
