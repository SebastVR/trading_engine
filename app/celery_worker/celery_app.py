"""
Celery Application Configuration
"""
from celery import Celery
from celery.schedules import crontab
from app.config.settings import settings

# Configurar Celery
celery_app = Celery(
    "trading_engine",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.celery_worker.tasks"]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos máximo por tarea
)

# Configurar tareas periódicas con Celery Beat
celery_app.conf.beat_schedule = {
    "monitor-market-every-15min": {
        "task": "app.celery_worker.tasks.monitor_market_signals",
        "schedule": crontab(minute="*/15"),  # Cada 15 minutos
        "args": (),
    },
    "monitor-market-simple-every-5min": {
        "task": "app.celery_worker.tasks.monitor_market_signals_simple",
        "schedule": crontab(minute="*/5"),  # Cada 5 minutos (más frecuente)
        "args": (),
    },
}

if __name__ == "__main__":
    celery_app.start()
