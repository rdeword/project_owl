"""
Главный файл приложения
"""
import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from backend.config.settings import get_settings
from backend.models.database import init_db
from backend.bots.main_bot import main_bot
from backend.services.telethon_monitor import telethon_monitor

settings = get_settings()

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting News Aggregator...")
    
    try:
        # Инициализация базы данных
        await init_db()
        logger.info("Database initialized")
        
        # Запуск главного бота
        asyncio.create_task(main_bot.start_polling())
        logger.info("Main bot started")
        
        # Запуск Telethon монитора
        asyncio.create_task(telethon_monitor.start())
        logger.info("Telethon monitor started")
        
        logger.info("Application started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down News Aggregator...")
    
    try:
        # Остановка Telethon монитора
        await telethon_monitor.stop()
        logger.info("Telethon monitor stopped")
        
        logger.info("Application stopped")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Создание FastAPI приложения
app = FastAPI(
    title="News Aggregator API",
    description="API для агрегации новостей из Telegram каналов",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение статических файлов для Web App
app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")


@app.get("/")
async def root():
    """Главная страница"""
    return {"message": "News Aggregator API", "status": "running"}


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "main_bot": "running",
            "telethon_monitor": "running",
            "database": "connected"
        }
    }


@app.get("/webapp")
async def webapp():
    """Web App интерфейс"""
    return FileResponse("webapp/index.html")


# API endpoints для Web App
@app.get("/api/v1/stats")
async def get_stats():
    """Получение статистики системы"""
    try:
        from backend.services.user_service import UserService
        from backend.models.database import get_db
        
        user_service = UserService()
        async for db in get_db():
            stats = await user_service.get_system_stats(db)
            return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"error": "Failed to get stats"}


def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


async def main():
    """Главная функция"""
    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Запуск сервера
        config = uvicorn.Config(
            app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower(),
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
