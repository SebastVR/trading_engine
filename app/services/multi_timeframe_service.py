"""
Multi-Timeframe Analysis Service
Analiza múltiples timeframes para confirmar señales de trading
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from app.services.market_service import MarketService
from app.services.trade_manager import StrategyEngine
from app.enums.trade_enums import SignalType


class TimeframeWeight(Enum):
    """Peso de cada timeframe en el análisis"""
    TIMEFRAME_15M = 1
    TIMEFRAME_1H = 2
    TIMEFRAME_4H = 3
    TIMEFRAME_1D = 4


@dataclass
class TimeframeSignal:
    """Señal de un timeframe individual"""
    timeframe: str
    signal: Optional[SignalType]
    price: float
    confidence: float
    details: Dict
    weight: int


@dataclass
class MultiTimeframeAnalysis:
    """Resultado del análisis multi-timeframe"""
    consensus_signal: Optional[SignalType]
    confidence_score: float
    timeframe_signals: List[TimeframeSignal]
    long_votes: int
    short_votes: int
    neutral_votes: int
    weighted_score: float
    recommendation: str


class MultiTimeframeService:
    """
    Servicio para análisis de múltiples timeframes
    """
    
    # Configuración de timeframes a analizar
    TIMEFRAMES = ["15m", "1h", "4h", "1d"]
    
    # Pesos de cada timeframe
    WEIGHTS = {
        "15m": TimeframeWeight.TIMEFRAME_15M.value,
        "1h": TimeframeWeight.TIMEFRAME_1H.value,
        "4h": TimeframeWeight.TIMEFRAME_4H.value,
        "1d": TimeframeWeight.TIMEFRAME_1D.value,
    }
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.market_service = MarketService()
    
    async def analyze_all_timeframes(self) -> MultiTimeframeAnalysis:
        """
        Analiza todos los timeframes configurados y genera consenso
        """
        print("\n" + "=" * 80)
        print("🔍 ANÁLISIS MULTI-TIMEFRAME")
        print("=" * 80)
        
        # Analizar cada timeframe secuencialmente con delay para evitar rate limit
        timeframe_signals = []
        for i, tf in enumerate(self.TIMEFRAMES):
            signal = await self._analyze_single_timeframe(tf)
            timeframe_signals.append(signal)
            # Añadir delay entre requests (excepto el último)
            if i < len(self.TIMEFRAMES) - 1:
                await asyncio.sleep(0.3)  # 300ms entre requests
        
        # Contar votos
        long_votes = sum(1 for ts in timeframe_signals if ts.signal == SignalType.LONG)
        short_votes = sum(1 for ts in timeframe_signals if ts.signal == SignalType.SHORT)
        neutral_votes = sum(1 for ts in timeframe_signals if ts.signal is None)
        
        # Calcular score ponderado
        weighted_score = self._calculate_weighted_score(timeframe_signals)
        
        # Determinar consenso
        consensus_signal = self._determine_consensus(
            timeframe_signals, 
            long_votes, 
            short_votes
        )
        
        # Calcular confianza
        confidence_score = self._calculate_confidence(
            consensus_signal,
            timeframe_signals,
            weighted_score
        )
        
        # Generar recomendación
        recommendation = self._generate_recommendation(
            consensus_signal,
            confidence_score,
            long_votes,
            short_votes,
            neutral_votes
        )
        
        # Imprimir resumen
        self._print_analysis_summary(
            timeframe_signals,
            consensus_signal,
            confidence_score,
            long_votes,
            short_votes,
            neutral_votes,
            weighted_score
        )
        
        return MultiTimeframeAnalysis(
            consensus_signal=consensus_signal,
            confidence_score=confidence_score,
            timeframe_signals=timeframe_signals,
            long_votes=long_votes,
            short_votes=short_votes,
            neutral_votes=neutral_votes,
            weighted_score=weighted_score,
            recommendation=recommendation
        )
    
    async def _analyze_single_timeframe(self, timeframe: str) -> TimeframeSignal:
        """
        Analiza un timeframe individual
        """
        try:
            # Obtener datos de mercado
            df = await self.market_service.get_klines_df(
                symbol=self.symbol,
                timeframe=timeframe,
                limit=300
            )
            
            # Analizar con estrategia (sin logs detallados)
            engine = StrategyEngine(df, timeframe, verbose=False)
            signal_dict = engine.compute_signal()
            signal = signal_dict.get("signal")
            entry_price = signal_dict.get("entry")
            stop_loss = signal_dict.get("stop_loss")
            take_profit = signal_dict.get("take_profit")
            
            # Calcular confianza basada en confirmaciones
            confidence = self._calculate_timeframe_confidence(engine, signal)
            
            # Obtener detalles
            details = {
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "confirmations": self._get_confirmations_summary(engine)
            }
            
            return TimeframeSignal(
                timeframe=timeframe,
                signal=signal,
                price=entry_price if entry_price else df['close'].iloc[-1],
                confidence=confidence,
                details=details,
                weight=self.WEIGHTS[timeframe]
            )
            
        except Exception as e:
            print(f"❌ Error analizando {timeframe}: {e}")
            return TimeframeSignal(
                timeframe=timeframe,
                signal=None,
                price=0,
                confidence=0,
                details={"error": str(e)},
                weight=self.WEIGHTS[timeframe]
            )
    
    def _calculate_timeframe_confidence(
        self, 
        engine: StrategyEngine, 
        signal: Optional[SignalType]
    ) -> float:
        """
        Calcula la confianza de la señal de un timeframe
        basada en cuántas confirmaciones pasaron
        """
        if signal is None:
            return 0.0
        
        # Contabilizar confirmaciones
        confirmations = 0
        total = 4  # trend, breakout, rsi, atr
        
        # Estas son propiedades que deberían estar en el engine
        # Por ahora usamos una estimación simple
        
        # Si hay señal, asumimos que al menos pasó la mitad
        if signal == SignalType.LONG:
            confirmations = 3  # típicamente: trend, rsi, atr (falta breakout)
        elif signal == SignalType.SHORT:
            confirmations = 3
        
        return (confirmations / total) * 100
    
    def _get_confirmations_summary(self, engine: StrategyEngine) -> Dict:
        """
        Obtiene resumen de confirmaciones del engine
        """
        # Por ahora retornamos info básica
        # En el futuro podríamos exponer más detalles del engine
        return {
            "trend": "calculated",
            "breakout": "calculated",
            "rsi": "calculated",
            "atr": "calculated"
        }
    
    def _calculate_weighted_score(
        self, 
        timeframe_signals: List[TimeframeSignal]
    ) -> float:
        """
        Calcula score ponderado dando más peso a timeframes largos
        
        LONG = +1, SHORT = -1, NEUTRAL = 0
        Multiplicado por el peso del timeframe
        """
        total_weight = sum(ts.weight for ts in timeframe_signals)
        weighted_sum = 0
        
        for ts in timeframe_signals:
            if ts.signal == SignalType.LONG:
                weighted_sum += ts.weight
            elif ts.signal == SignalType.SHORT:
                weighted_sum -= ts.weight
            # NEUTRAL = 0, no afecta
        
        # Normalizar a rango -100 a +100
        if total_weight > 0:
            return (weighted_sum / total_weight) * 100
        return 0
    
    def _determine_consensus(
        self,
        timeframe_signals: List[TimeframeSignal],
        long_votes: int,
        short_votes: int
    ) -> Optional[SignalType]:
        """
        Determina el consenso basado en votos y pesos
        
        Reglas:
        1. Requiere al menos 2 timeframes con la misma señal
        2. Si hay empate, usa el weighted_score para decidir
        3. Si weighted_score está muy cerca de 0, no hay consenso
        """
        
        # Regla 1: Requiere al menos 2 votos
        if long_votes >= 2 and long_votes > short_votes:
            return SignalType.LONG
        
        if short_votes >= 2 and short_votes > long_votes:
            return SignalType.SHORT
        
        # Si hay empate o no hay suficientes votos, usar weighted_score
        weighted_score = self._calculate_weighted_score(timeframe_signals)
        
        # Umbral: si el score ponderado es fuerte, puede haber consenso
        if weighted_score > 30:  # Fuerte inclinación LONG
            return SignalType.LONG
        elif weighted_score < -30:  # Fuerte inclinación SHORT
            return SignalType.SHORT
        
        # Sin consenso claro
        return None
    
    def _calculate_confidence(
        self,
        consensus_signal: Optional[SignalType],
        timeframe_signals: List[TimeframeSignal],
        weighted_score: float
    ) -> float:
        """
        Calcula la confianza del consenso (0-100%)
        
        Factores:
        - Cuántos timeframes coinciden
        - Peso de los timeframes que coinciden
        - Magnitud del weighted_score
        """
        if consensus_signal is None:
            return 0.0
        
        # Contar timeframes que coinciden con el consenso
        matching_signals = [
            ts for ts in timeframe_signals 
            if ts.signal == consensus_signal
        ]
        
        # Calcular peso total que coincide
        matching_weight = sum(ts.weight for ts in matching_signals)
        total_weight = sum(ts.weight for ts in timeframe_signals)
        
        # Porcentaje de peso que coincide (0-100)
        weight_confidence = (matching_weight / total_weight) * 100
        
        # Confianza basada en score ponderado (0-100)
        score_confidence = min(abs(weighted_score), 100)
        
        # Promedio de ambos factores
        return (weight_confidence + score_confidence) / 2
    
    def _generate_recommendation(
        self,
        consensus_signal: Optional[SignalType],
        confidence_score: float,
        long_votes: int,
        short_votes: int,
        neutral_votes: int
    ) -> str:
        """
        Genera recomendación textual basada en el análisis
        """
        if consensus_signal is None:
            return (
                "⚠️ SIN CONSENSO - Los timeframes están en conflicto. "
                "Esperar confirmación antes de operar."
            )
        
        signal_text = "LONG (comprar)" if consensus_signal == SignalType.LONG else "SHORT (vender)"
        
        if confidence_score >= 70:
            strength = "FUERTE"
            icon = "🟢"
        elif confidence_score >= 50:
            strength = "MODERADA"
            icon = "🟡"
        else:
            strength = "DÉBIL"
            icon = "🟠"
        
        return (
            f"{icon} Señal {signal_text} - Confianza {strength} ({confidence_score:.1f}%)\n"
            f"   Votos: {long_votes} LONG, {short_votes} SHORT, {neutral_votes} NEUTRAL"
        )
    
    def _print_analysis_summary(
        self,
        timeframe_signals: List[TimeframeSignal],
        consensus_signal: Optional[SignalType],
        confidence_score: float,
        long_votes: int,
        short_votes: int,
        neutral_votes: int,
        weighted_score: float
    ):
        """
        Imprime resumen del análisis multi-timeframe
        """
        print(f"\n📊 Símbolo: {self.symbol}")
        print(f"⏰ Timeframes analizados: {len(timeframe_signals)}")
        print("\n" + "-" * 80)
        
        # Tabla de señales por timeframe
        print("\n📈 SEÑALES POR TIMEFRAME:")
        print(f"{'Timeframe':<12} {'Señal':<10} {'Precio':<12} {'Confianza':<12} {'Peso':<6}")
        print("-" * 80)
        
        for ts in sorted(timeframe_signals, key=lambda x: x.weight):
            signal_text = "NEUTRAL" if ts.signal is None else ts.signal.value
            signal_icon = "⚪" if ts.signal is None else ("🟢" if ts.signal == SignalType.LONG else "🔴")
            
            print(
                f"{ts.timeframe:<12} "
                f"{signal_icon} {signal_text:<8} "
                f"${ts.price:>10,.2f} "
                f"{ts.confidence:>6.1f}% "
                f"(x{ts.weight})"
            )
        
        print("\n" + "-" * 80)
        
        # Resultados del consenso
        print("\n🎯 CONSENSO MULTI-TIMEFRAME:")
        print(f"   📊 Votos: {long_votes} LONG, {short_votes} SHORT, {neutral_votes} NEUTRAL")
        print(f"   ⚖️  Score Ponderado: {weighted_score:+.1f}")
        
        if consensus_signal:
            signal_text = consensus_signal.value
            signal_icon = "🟢" if consensus_signal == SignalType.LONG else "🔴"
            print(f"   {signal_icon} Señal de Consenso: {signal_text}")
            print(f"   💪 Confianza: {confidence_score:.1f}%")
        else:
            print(f"   ⚪ Señal de Consenso: SIN CONSENSO")
            print(f"   ⚠️  Confianza: {confidence_score:.1f}%")
        
        print("\n" + "=" * 80)
