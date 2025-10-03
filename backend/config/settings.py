"""
Настройки приложения
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot Tokens
    main_bot_token: str = Field(..., env="MAIN_BOT_TOKEN")
    test_user_bot_1: Optional[str] = Field(None, env="TEST_USER_BOT_1")
    test_user_bot_2: Optional[str] = Field(None, env="TEST_USER_BOT_2")
    
    # Telegram API (для Telethon)
    telegram_api_id: int = Field(..., env="TELEGRAM_API_ID")
    telegram_api_hash: str = Field(..., env="TELEGRAM_API_HASH")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    
    # OpenAI API
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Web App
    webapp_url: str = Field("http://localhost:8000/webapp", env="WEBAPP_URL")
    
    # Server settings
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(True, env="DEBUG")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/app.log", env="LOG_FILE")
    
    # Security
    secret_key: str = Field("your-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret_key: str = Field("your-jwt-secret-key-change-in-production", env="JWT_SECRET_KEY")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(10, env="RATE_LIMIT_BURST")
    
    # Bot settings
    bot_username_prefix: str = "NewsBot"
    max_channels_per_user: int = 50
    max_categories_per_user: int = 20
    
    # News processing
    news_batch_size: int = 100
    news_processing_interval: int = 300  # 5 минут
    
    # AI settings
    ai_summary_max_length: int = 500
    ai_categorization_confidence_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Создаем глобальный экземпляр настроек
settings = Settings()


def get_settings() -> Settings:
    """Получить настройки приложения"""
    return settings
