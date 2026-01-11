from fastapi import FastAPI
from app.config.settings import settings
from app.middleware.logging import setup_logging_middleware
from app.routers.trade_router import router as trade_router
from app.routers.multi_timeframe_router import router as multi_timeframe_router
from app.routers.simple_signal_router import router as simple_signal_router
from app.routers.test_router import router as test_router
from app.routers.ai_router import router as ai_router
from app.controllers.health_controller import router as health_router
from app.db.session import init_db
from app.services.trade_manager import TradeManager

api = FastAPI(title=settings.APP_NAME)

setup_logging_middleware(api)

api.include_router(health_router, tags=["health"])
api.include_router(trade_router, prefix="/trades", tags=["trades"])
api.include_router(multi_timeframe_router, tags=["multi-timeframe"])
api.include_router(simple_signal_router, tags=["simple-signal"])
api.include_router(test_router, tags=["testing"])
api.include_router(ai_router, tags=["ai"])

_trade_manager: TradeManager | None = None


@api.on_event("startup")
async def on_startup():
    await init_db()
    global _trade_manager
    _trade_manager = TradeManager()
    await _trade_manager.start()


@api.on_event("shutdown")
async def on_shutdown():
    global _trade_manager
    if _trade_manager:
        await _trade_manager.stop()
        _trade_manager = None