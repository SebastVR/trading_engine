# 🚀 NIGHT TEST - Resumen de Configuración

## ✅ Sistema Listo para Correr Toda la Noche

### 📊 Configuración Actual

**Rama**: `feature/single-timeframe` (Modo Experimental: Simple + Multi-Timeframe)

**Dos Modos Ejecutándose en Paralelo**:

1. **Modo MULTI-TIMEFRAME** (cada 15 minutos)
   - Analiza: 15m, 1h, 4h, 1d
   - Requiere: Consenso ≥40% (2 de 4 timeframes)
   - Endpoint: `GET /trades/multi-signal`
   - Confiabilidad: Alta (menos falsos positivos)

2. **Modo SIMPLE** (cada 5 minutos)
   - Analiza: Solo 15m
   - Requiere: Solo confirmación técnica (sin consenso)
   - Endpoint: `GET /trades/simple-signal`
   - Velocidad: 3x más rápido (cada 5 min vs 15 min)

### 🔔 Alertas Telegram

**Verificado**: ✅ Telegram está configurado y funcionando
- Token: Válido
- Chat ID: Activo
- Test enviado: 2026-01-09 04:09:20 UTC

**Tipos de Alertas a Recibir**:
- 📈 Señal LONG (cuando 2+ timeframes o 15m técnico generan LONG)
- 📉 Señal SHORT (cuando 2+ timeframes o 15m técnico generan SHORT)
- Incluyen: Entry, Stop Loss, Take Profit, Confianza%

### 🎯 Qué Esperar Esta Noche

#### Escenario 1: Mercado Lateral (Probable)
- Pocas o ninguna señal
- Ambos modos mostrarán NEUTRAL
- Confirmación: El problema es el mercado, no el sistema

#### Escenario 2: Tendencia Fuerte (Ideal)
- Modo SIMPLE: Múltiples señales (5 min después de movimiento)
- Modo MULTI: Señal con alta confianza (consenso más fuerte)
- Telegram: Recibirás alertas automáticas

#### Escenario 3: Breakout Rápido
- Modo SIMPLE: Captura primero (velocidad)
- Modo MULTI: Confirma después (confiabilidad)
- Permite comparar efectividad de cada enfoque

### 📋 Checklist Pre-Noche

- [x] Contenedores corriendo (5/5 healthy)
- [x] API en puerto 85
- [x] Celery Worker conectado a Redis
- [x] Celery Beat ejecutando tareas
- [x] Telegram configurado y probado
- [x] Ambos endpoints accesibles
- [x] Logs en background

### 🔗 Endpoints Disponibles

```bash
# Obtener señal simple (15m sin consenso)
curl http://localhost:85/trades/simple-signal

# Obtener señal multi (4 timeframes con consenso)
curl http://localhost:85/trades/multi-signal

# Enviar alerta de prueba
curl -X POST http://localhost:85/trades/test-alert

# Ver logs en vivo
docker compose logs -f celery_worker celery_beat
```

### 📊 Métricas a Monitorear

Durante la noche, registra:

| Métrica | Descripción |
|---------|-------------|
| Hora de Señal | Timestamp exacto |
| Tipo | LONG / SHORT |
| Fuente | Simple / Multi |
| Confianza | Porcentaje |
| Precio Entry | Precio exacto |
| SL | Stop Loss |
| TP | Take Profit |
| Resultado | ¿Se alcanzó TP o SL? |

### 💡 Objetivo

**Determinar**: ¿Qué modo es mejor?
- Modo SIMPLE: Más velocidad, más señales
- Modo MULTI: Más confiabilidad, menos ruido

**Resultado final**: Merge a main con la decisión final

---

## 🌙 Status del Sistema

**Iniciado**: 2026-01-09 04:09:00 UTC
**Duración**: 8-10 horas (toda la noche)
**Resultado esperado**: Mañana por la mañana

Mantén los logs abiertos en la terminal para ver cada ciclo de monitoreo 📺
