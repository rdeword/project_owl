"""
Настройка подключения к базе данных
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from backend.config.settings import get_settings

settings = get_settings()

# Создаем базовый класс для моделей
Base = declarative_base()

# Синхронный движок для миграций
sync_engine = create_engine(
    settings.database_url.replace("postgresql://", "postgresql+psycopg2://"),
    echo=settings.debug,
    poolclass=NullPool if settings.debug else None
)

# Асинхронный движок для приложения
async_engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    poolclass=NullPool if settings.debug else None
)

# Фабрика сессий
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """Получить сессию базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных"""
    async with async_engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
