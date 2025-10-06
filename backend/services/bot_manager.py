"""
Менеджер ботов - создание и управление личными ботами пользователей
"""
import asyncio
import logging
import httpx
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.settings import get_settings
from backend.models.models import UserBot
from backend.services.user_service import UserService

settings = get_settings()
logger = logging.getLogger(__name__)


class BotManager:
    """Менеджер ботов"""
    
    def __init__(self):
        self.user_service = UserService()
        self.botfather_url = "https://api.telegram.org/bot"
        self.botfather_token = settings.main_bot_token  # Используем токен главного бота
    
    async def assign_bot_to_user(self, user_id: int, user_name: str) -> Optional[Dict[str, Any]]:
        """
        Назначение бота из пула пользователю
        
        Args:
            user_id: ID пользователя
            user_name: Имя пользователя
            
        Returns:
            Информация о назначенном боте или None при ошибке
        """
        try:
            # Получаем свободного бота из пула
            bot_info = await self._get_available_bot_from_pool()
            
            if not bot_info:
                logger.error(f"No available bots in pool for user {user_id}")
                return None
            
            # Сохраняем информацию о назначении в базу данных
            async for db in get_db():
                user_bot = UserBot(
                    user_id=user_id,
                    bot_token=bot_info['token'],
                    bot_username=bot_info['username'],
                    is_active=True
                )
                db.add(user_bot)
                await db.commit()
                await db.refresh(user_bot)
                
                logger.info(f"Assigned bot {bot_info['username']} to user {user_id}")
                return {
                    'id': user_bot.id,
                    'username': bot_info['username'],
                    'token': bot_info['token']
                }
                
        except Exception as e:
            logger.error(f"Error assigning bot to user {user_id}: {e}")
            return None
    
    async def _get_available_bot_from_pool(self) -> Optional[Dict[str, Any]]:
        """
        Получение свободного бота из пула
        
        Returns:
            Информация о свободном боте или None если пул пуст
        """
        try:
            # Получаем свободного бота из пула предварительно созданных ботов
            # В реальной реализации здесь будет запрос к базе данных
            logger.info("Getting available bot from pool")
            
            # Заглушка - в реальности нужно получать из базы данных
            return {
                'username': f"userbot_{user_id}",
                'token': f"123456789:ABCdefGHIjklMNOpqrsTUVwxyz{user_id}",
                'display_name': f"User Bot {user_id}"
            }
            
        except Exception as e:
            logger.error(f"Error getting bot from pool: {e}")
            return None
    
    async def get_user_bot(self, user_id: int) -> Optional[UserBot]:
        """
        Получение бота пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Бот пользователя или None
        """
        try:
            async for db in get_db():
                return await self.user_service.get_user_bot(db, user_id)
        except Exception as e:
            logger.error(f"Error getting user bot for user {user_id}: {e}")
            return None
    
    async def deactivate_user_bot(self, user_id: int) -> bool:
        """
        Деактивация бота пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если успешно, False иначе
        """
        try:
            async for db in get_db():
                user_bot = await self.user_service.get_user_bot(db, user_id)
                if user_bot:
                    user_bot.is_active = False
                    await db.commit()
                    logger.info(f"Deactivated bot for user {user_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deactivating bot for user {user_id}: {e}")
            return False
    
    async def get_all_active_bots(self) -> list[UserBot]:
        """
        Получение всех активных ботов
        
        Returns:
            Список активных ботов
        """
        try:
            async for db in get_db():
                return await self.user_service.get_all_active_bots(db)
        except Exception as e:
            logger.error(f"Error getting all active bots: {e}")
            return []
