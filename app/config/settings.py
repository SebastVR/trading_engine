from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    APP_NAME: str
    ENVIRONMENT: str
    LOG_LEVEL: str

    # Postgres config (debe coincidir con .env)
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_URL: str

    SYMBOL: str
    TIMEFRAME: str
    POLL_SECONDS: int
    CANDLES_LIMIT: int

    RISK_REWARD: float
    ATR_MULTIPLIER_SL: float

    MA_FAST: int
    MA_SLOW: int

    RSI_PERIOD: int
    RSI_MIN: int
    RSI_MAX: int

    BINANCE_TAKER_FEE: float
    BINANCE_MAKER_FEE: float

    BINANCE_API_KEY: str | None = None
    BINANCE_API_SECRET: str | None = None

    ALERT_MODE: str

    # Telegram config
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    # Celery config
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    AI_ENABLED: bool = False
    AI_PROVIDER: str  # gemini | openai | bedrock
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_TEMPERATURE: float = 0.2

    # AWS Bedrock Configuration (FASE 1: IA Filter)
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION_NAME: str = "us-east-1"
    BEDROCK_MODEL: str = "openai.gpt-oss-120b-1:0"

    # IA Filter Settings
    AI_QUALITY_THRESHOLD: float = 75.0
    # Si está activo, el sistema SOLO enviará/guardará señales cuando la IA apruebe.
    # (Esto permite cortar de inmediato el ruido de señales de baja calidad)
    AI_FILTER_ENFORCE: bool = False
    AI_TEMPERATURE_FILTER: float = 0.3
    AI_MAX_TOKENS: int = 1000

    # Trading safeguards (optimización FASE 1)
    DISABLE_SHORTS: bool = False
    # Filtrar señales por ventana horaria (hora Colombia). Ej: "7-17,19-20".
    # Vacío = no filtra.
    SIGNAL_ALLOWED_HOURS_CO: str = ""

    class Config:
        env_file = ".env"


settings = Settings()


def get_settings() -> Settings:
    """
    Función helper para obtener settings (útil para Celery y otros contextos)
    """
    return settings
