import time
from fastapi import Request, FastAPI
from app.config.settings import settings


def setup_logging_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        print(f"[{settings.APP_NAME}] {request.method} {request.url.path} -> {response.status_code} ({elapsed:.1f}ms)")
        return response
