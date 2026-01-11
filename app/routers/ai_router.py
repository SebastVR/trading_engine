"""
AI Router: Endpoints HTTP para IA Filter
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.controllers import ai_controller


router = APIRouter(prefix="/ai", tags=["AI"])


class SignalValidationRequest(BaseModel):
    """Request para validar signal."""

    signal: Dict[str, Any]
    symbol: str
    timeframe: str
    market_context: Optional[Dict[str, Any]] = None


class SignalValidationResponse(BaseModel):
    """Response de validación de signal."""

    quality_score: float
    confidence: str
    recommendation: str
    should_open: bool
    confluences: list = []
    risks: list = []
    reasoning: str


@router.post("/validate-signal")
async def validate_signal(
    request: SignalValidationRequest,
) -> SignalValidationResponse:
    """
    Valida una señal de trading usando IA.

    Ejemplo de request:
    ```json
    {
      "signal": {
        "signal": "short",
        "entry": 90511.02,
        "stop_loss": 91729.72,
        "take_profit": 88073.60,
        "confirmations": {
          "trend": "down",
          "rsi": 45.2,
          "atr": 62.4
        }
      },
      "symbol": "BTCUSDT",
      "timeframe": "15m"
    }
    ```
    """
    return await ai_controller.validate_signal_quality(
        signal=request.signal,
        symbol=request.symbol,
        timeframe=request.timeframe,
        market_context=request.market_context,
    )


@router.get("/insights")
async def get_insights() -> Dict[str, Any]:
    """Obtiene insights generales del sistema de IA."""
    return await ai_controller.get_ai_insights()


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """Obtiene estado del sistema de IA."""
    return {
        "status": "operational",
        "phase": "PHASE_1_FILTER",
        "provider": "aws_bedrock",
        "model": "openai.gpt-oss-120b-1:0",
        "quality_threshold": 75,
        "message": "IA Filter activo - validando signals antes de abrir trades",
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check del servicio de IA."""
    return {"status": "healthy", "service": "trading_ai_agent"}
