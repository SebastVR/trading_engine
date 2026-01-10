# 🚀 GUÍA DE USO Y MONITOREO - Trading Engine

## ✅ Estado Actual

- **Sistema:** Activo y funcionando
- **Servicios:** 5/5 contenedores corriendo
- **Trades guardados:** 18+
- **Señales/día:** 3-5
- **Horarios:** Sincronizados (Colombia UTC-5)

---

## 📊 Comandos Útiles

### Ver logs en tiempo real
```bash
cd /home/integral/DevUser/trading_engine
docker compose logs -f celery_worker
```

### Filtrar solo señales importantes
```bash
docker compose logs -f celery_worker 2>&1 | grep -E "GENERANDO SEÑAL|Mensaje enviado|Trade guardado|Error"
```

### Ver todos los trades guardados
```bash
curl -s http://localhost:85/trades | python3 -m json.tool
```

### Ver último trade generado
```bash
curl -s http://localhost:85/trades | python3 -m json.tool | head -50
```

### Generar señal de prueba (testing)
```bash
curl -s http://localhost:85/trades/simple-signal | python3 -m json.tool
```

### Ver salud del API
```bash
curl -s http://localhost:85/health | python3 -m json.tool
```

---

## 🔄 Gestión de Servicios

### Parar todos los servicios
```bash
cd /home/integral/DevUser/trading_engine
docker compose down
```

### Levantar servicios
```bash
docker compose up -d
```

### Reiniciar un servicio específico
```bash
docker compose restart celery_worker
```

### Ver logs de un servicio específico
```bash
docker compose logs -f api          # API REST
docker compose logs -f celery_worker  # Worker (señales)
docker compose logs -f celery_beat    # Scheduler
docker compose logs -f db           # PostgreSQL
docker compose logs -f redis        # Redis
```

---

## 📈 Monitoreo

### Métricas clave a seguir

1. **Frecuencia de señales:**
   - Expected: 3-5 por día
   - Ubicación: logs de celery_worker

2. **Telegram delivery:**
   - Expected: 100% (HTTP 200 OK)
   - Error: Check formato del mensaje

3. **BD persistence:**
   - Expected: 100% de señales guardadas
   - Ubicación: Endpoint `/trades`

4. **Trade closure:**
   - Expected: Cierre automático por SL/TP
   - Ubicación: Status de trade = "closed"

5. **PnL tracking:**
   - Expected: Cada trade cerrado tiene resultado
   - Ubicación: `pnl_abs` y `pnl_pct` en BD

---

## 🔍 Troubleshooting

### Problema: No se generan señales
```bash
# 1. Ver logs
docker compose logs celery_worker | grep -E "GENERANDO|FALTA"

# 2. Verificar parámetros en app/services/trade_manager.py
# 3. Revisar precio actual vs thresholds
```

### Problema: Errores en Telegram
```bash
# Ver error específico
docker compose logs celery_worker | grep "Error Telegram"

# Posibles causas:
# - Token incorrecto
# - Chat ID incorrecto
# - Formato de mensaje (HTML vs Markdown)
```

### Problema: Trades no se guardan en BD
```bash
# Ver error de BD
docker compose logs celery_worker | grep "Error guardando trade"

# Posibles causas:
# - Conflicto de event loops (resuelto con ThreadPoolExecutor)
# - Conexión DB caída
# - Esquema de tabla incorrecto
```

### Problema: Desincronización de horarios
```bash
# Verificar horario en mensaje vs BD
curl -s http://localhost:85/trades | python3 -m json.tool | grep "opened_at"

# Debe estar en UTC-5 (Colombia)
# Si está en UTC, revisar _get_timestamp() en telegram_service.py
```

---

## 💾 Base de Datos

### Conectarse a PostgreSQL
```bash
psql -h localhost -p 5435 -U postgres -d trading_engine
```

### Ver tabla de trades
```sql
SELECT id, symbol, side, entry_price, status, opened_at 
FROM trades 
ORDER BY id DESC 
LIMIT 10;
```

### Contar trades abiertos
```sql
SELECT COUNT(*) FROM trades WHERE status = 'open';
```

### Ver PnL de trades cerrados
```sql
SELECT id, symbol, side, entry_price, close_price, result, pnl_pct 
FROM trades 
WHERE status = 'closed' 
ORDER BY closed_at DESC 
LIMIT 10;
```

---

## 📝 Archivos Principales

```
trading_engine/
├── app/
│   ├── services/
│   │   ├── telegram_service.py       # Alertas (UTC-5)
│   │   └── trade_manager.py          # Monitoreo y parámetros
│   ├── controllers/
│   │   ├── simple_signal_controller.py    # Señales 15m
│   │   └── multi_timeframe_controller.py  # Consenso multi-TF
│   ├── celery_worker/
│   │   └── tasks.py                  # Tareas automáticas
│   └── config/
│       └── settings.py               # Configuración
├── docker-compose.yml
├── SISTEMA_ESTADO_FINAL.md           # Estado actual
├── RESUMEN_CAMBIOS_DIA.md            # Lo que cambió
└── README.md                         # Documentación
```

---

## ⚙️ Configuración

**Archivo:** `app/config/settings.py`

Parámetros clave:
```python
SYMBOL = "BTCUSDT"              # Par a tradear
LOOKBACK_PERIODS = 5            # Velas para breakout
HIGH_ATR_LOOKBACK = 3           # Velas en alta volatilidad
ENTRY_ZONE_PCT = 0.003          # 0.3% zona entrada
BREAKOUT_THRESHOLD = 0.40       # 40% para consenso multi-TF
TELEGRAM_BOT_TOKEN = "..."      # Token Telegram
TELEGRAM_CHAT_ID = "..."        # ID chat Telegram
```

---

## 🚨 Alertas a monitorear

### Nivel Crítico (PARAR SISTEMA)
- PostgreSQL desconectada
- Redis desconectada
- API no responde

### Nivel Medio (REVISAR)
- Error en Telegram (Bad Request)
- Trade no se guarda en BD
- Conflicto de event loops

### Nivel Bajo (INFO)
- Precio fuera de rango esperado
- RSI en extremos
- ATR muy bajo

---

## 📞 Soporte Rápido

**Error más común:** "Bad Request: can't parse entities"
- **Causa:** Formato de mensaje incorrecto
- **Solución:** Revisar parse_mode (debe ser "Markdown")

**Problema frecuente:** No hay señales
- **Causa:** Parámetros demasiado estrictos
- **Solución:** Reducir lookback o entry_zone_pct

**Conflictos asyncio:**
- **Causa:** Mezcla de async/sync en Celery
- **Solución:** Ya está resuelto con ThreadPoolExecutor

---

## ✅ Checklist diario

- [ ] Sistema levantado (docker compose up -d)
- [ ] 5 servicios corriendo (docker compose ps)
- [ ] Trades siendo generados (curl /trades/simple-signal)
- [ ] Señales llegando a Telegram (revisar chat)
- [ ] Trades guardándose en BD (curl /trades)
- [ ] Sin errores en logs (docker compose logs)

---

**Última actualización:** 10 de Enero 2026
**Estado:** ✅ Completamente funcional
