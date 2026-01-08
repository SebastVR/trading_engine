#!/bin/bash

# Script de monitoreo del Trading Engine
# Uso: ./check_signals.sh

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              🤖 TRADING ENGINE - ESTADO DEL SISTEMA                 ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar si los contenedores están corriendo
echo "📦 Estado de contenedores:"
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "⚠️  Docker compose no disponible"
echo ""

# Verificar health
echo "💚 Health Check:"
HEALTH=$(curl -s http://localhost:85/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ API funcionando correctamente"
else
    echo "   ❌ API no responde"
    exit 1
fi
echo ""

# Obtener precio actual
echo "💰 Precio Actual:"
curl -s http://localhost:85/trades/signal | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'   {d[\"symbol\"]}: \${d[\"now_price\"]:,.2f}')
except:
    print('   ⚠️  Error obteniendo precio')
"
echo ""

# Análisis multi-timeframe
echo "🎯 Consenso Multi-Timeframe:"
curl -s http://localhost:85/trades/multi-signal | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    c = d['consensus']
    v = d['votes']
    
    signal = c['signal']
    if signal:
        icon = '🟢' if signal == 'LONG' else '🔴'
        print(f'   {icon} Señal: {signal}')
        print(f'   💪 Confianza: {c[\"confidence\"]:.1f}%')
        print(f'   📊 Votos: {v[\"long\"]} LONG, {v[\"short\"]} SHORT, {v[\"neutral\"]} NEUTRAL')
        
        if 'trading_setup' in d:
            ts = d['trading_setup']
            print(f'')
            print(f'   💰 Setup de Trading:')
            print(f'      Entry: \${ts[\"entry_price\"]:,.2f}')
            print(f'      Stop Loss: \${ts[\"stop_loss\"]:,.2f}')
            print(f'      Take Profit: \${ts[\"take_profit\"]:,.2f}')
            print(f'      R:R = 1:{ts[\"risk_reward_ratio\"]:.2f}')
            print(f'')
            print(f'   🔥 ¡HAY SEÑAL! Revisa Telegram o ve a Binance')
    else:
        print(f'   ⚪ Sin consenso (esperando confirmación)')
        print(f'   📊 Votos: {v[\"long\"]} LONG, {v[\"short\"]} SHORT, {v[\"neutral\"]} NEUTRAL')
except Exception as e:
    print(f'   ⚠️  Error: {e}')
"
echo ""

# Verificar Telegram
echo "📱 Telegram:"
curl -s http://localhost:85/test/telegram | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d['success']:
        print('   ✅ Configurado y funcionando')
        print('   📨 Recibirás alertas cuando haya consenso ≥50%')
    else:
        print('   ❌ No configurado')
except:
    print('   ⚠️  Error verificando Telegram')
"
echo ""

# Últimas 5 líneas de logs
echo "📋 Últimos logs:"
docker logs trading_engine_api --tail 5 2>&1 | grep -v "INFO:" | head -5
echo ""

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Sistema funcionando - Monitoreando mercado 24/7                 ║"
echo "║  📱 Recibirás alerta en Telegram cuando haya señal con alta conf.   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
