# 🔬 Comparación: Modo Multi-Timeframe vs Modo Simple

## 📊 Configuración Actual

### Modo MULTI-TIMEFRAME (15m, 1h, 4h, 1d)
- **Frecuencia**: Cada 15 minutos (Celery Beat)
- **Requisito**: Consenso ≥40% (2 de 4 timeframes coinciden)
- **Ventaja**: Señales más confiables, menos falsos positivos
- **Desventaja**: Menos señales totales

### Modo SIMPLE (Solo 15m)
- **Frecuencia**: Cada 5 minutos (Celery Beat) - 3x más frecuente
- **Requisito**: Solo análisis técnico 15m (sin consenso)
- **Ventaja**: Más señales, detección más rápida
- **Desventaja**: Mayor probabilidad de falsos positivos

---

## 🎯 Métricas a Medir

| Métrica | Descripción |
|---------|-------------|
| **Señales Totales** | Cuántas señales genera cada modo |
| **Tasa de Éxito** | Porcentaje que alcanzan TP vs SL |
| **Falsos Positivos** | Señales que resultan en pérdida rápida |
| **Tiempo Promedio en Posición** | Cuánto dura una posición ganadora/perdedora |
| **Relación R:R** | Riesgo vs Recompensa promedio |

---

## 📈 Observaciones en Vivo

### Ciclo 1: [Inicial]
- **Simple**: Sin señal (mercado neutral)
- **Multi**: Sin señal (mercado neutral)
- Consenso: ✅ Ambos acuerdan - mercado lateral

### Ciclo 2: [+5 min]
- Esperando...

---

## 💡 Hipótesis

**H1**: El modo simple generará 3x más señales
- Razón: Frecuencia 5min vs 15min, sin filtro de consenso

**H2**: El modo simple tendrá mayor % de falsos positivos
- Razón: Sin validación multi-timeframe

**H3**: En mercado lateral, ambos generarán pocas señales
- Razón: El 15m necesita confirmación de MA/breakout

**H4**: En mercado trending, el modo multi ganará confianza rápidamente
- Razón: 4 timeframes verán la misma dirección → 100% consenso

---

## 🔄 Próximos Pasos

1. **Dejar corriendo 2-3 horas** en ambos modos
2. **Registrar cada señal** con timestamp y resultado
3. **Comparar rentabilidad teórica** basada en SL/TP
4. **Decidir**: ¿Mantener Multi? ¿Cambiar a Simple? ¿Híbrido?

---

## 📝 Notas

- El sistema está en rama `feature/single-timeframe`
- Logs filtrados disponibles en: `docker compose logs celery_worker celery_beat`
- Endpoints:
  - Simple: `GET /trades/simple-signal`
  - Multi: `GET /trades/multi-signal`
