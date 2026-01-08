from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import settings

# Motor asíncrono para PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL, echo=False, pool_pre_ping=True
)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base declarativa para modelos ORM
class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Inicializa la base de datos (sin Alembic)."""
    from app.models.trade_model import Trade  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependencia para obtener una sesión asíncrona de la base de datos."""
    async with AsyncSessionLocal() as session:
        yield session
