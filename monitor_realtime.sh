#!/bin/bash

# Script para monitorear logs en tiempo real del trading engine
# Muestra solo los eventos importantes: señales, mensajes a Telegram, trades guardados

clear
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                     TRADING ENGINE - MONITOR EN TIEMPO REAL                    ║"
echo "║                                                                                ║"
echo "║  Mostrando:  ✅ Señales generadas                                             ║"
echo "║              📬 Mensajes a Telegram                                           ║"
echo "║              💾 Trades guardados en BD                                        ║"
echo "║              ❌ Errores (si los hay)                                          ║"
echo "║                                                                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Presiona Ctrl+C para salir..."
echo ""
echo "─────────────────────────────────────────────────────────────────────────────────"
echo ""

# Mostrar logs filtrados en tiempo real
docker compose logs -f celery_worker 2>&1 | grep -E "🎯 GENERANDO SEÑAL|✅ Mensaje enviado|✅ Trade guardado|❌ Error|⚠️"
