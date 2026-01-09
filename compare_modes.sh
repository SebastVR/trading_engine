#!/bin/bash

# Script para comparar Modo Multi-Timeframe vs Modo Simple

echo "=================================="
echo "🔬 COMPARACIÓN: Multi vs Simple"
echo "=================================="
echo ""
echo "Modo MULTI-TIMEFRAME (cada 15 min):"
echo "  - Requiere consenso de 2+ timeframes"
echo "  - Menos señales pero más confiables"
echo ""
echo "Modo SIMPLE (cada 5 min):"
echo "  - Solo análisis 15m"
echo "  - Más señales, menos filtrado"
echo ""
echo "Monitoreando por 10 minutos..."
echo "=================================="
echo ""

# Hacer 10 llamadas al endpoint simple (cada 1 min = cada 60 segundos)
for i in {1..10}; do
    echo "[$(date '+%H:%M:%S')] Ciclo $i/10"
    
    # Obtener señal simple
    simple_response=$(curl -s http://localhost:85/trades/simple-signal)
    simple_signal=$(echo "$simple_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('signal', 'NONE'))" 2>/dev/null || echo "ERROR")
    simple_price=$(echo "$simple_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('price', 0))" 2>/dev/null || echo "0")
    
    echo "  └─ SIMPLE: Señal=$simple_signal | Precio=\$$simple_price"
    
    # Obtener señal multi (menos frecuentemente)
    if [ $((i % 3)) -eq 0 ]; then
        multi_response=$(curl -s http://localhost:85/trades/multi-signal)
        multi_signal=$(echo "$multi_response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('consensus', {}).get('signal', 'NONE'))" 2>/dev/null || echo "ERROR")
        multi_conf=$(echo "$multi_response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('consensus', {}).get('confidence', 0))" 2>/dev/null || echo "0")
        echo "  └─ MULTI:  Señal=$multi_signal | Confianza=$multi_conf%"
    fi
    
    # Esperar 60 segundos para siguiente ciclo
    if [ $i -lt 10 ]; then
        echo ""
        sleep 60
    fi
done

echo ""
echo "=================================="
echo "✅ Comparación completada"
echo "=================================="
