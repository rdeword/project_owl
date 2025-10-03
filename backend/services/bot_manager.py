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
    
    async def create_user_bot(self, user_id: int, user_name: str) -> Optional[Dict[str, Any]]:
        """
        Создание личного бота для пользователя
        
        Args:
            user_id: ID пользователя
            user_name: Имя пользователя
            
        Returns:
            Информация о созданном боте или None при ошибке
        """
        try:
            # Генерируем имя бота
            bot_username = f"{settings.bot_username_prefix}{user_id}_{user_name.lower().replace(' ', '')}"
            
            # Создаем бота через BotFather API
            bot_info = await self._create_bot_via_botfather(bot_username, user_name)
            
            if not bot_info:
                logger.error(f"Failed to create bot for user {user_id}")
                return None
            
            # Сохраняем информацию о боте в базу данных
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
                
                logger.info(f"Created bot {bot_info['username']} for user {user_id}")
                return {
                    'id': user_bot.id,
                    'username': bot_info['username'],
                    'token': bot_info['token']
                }
                
        except Exception as e:
            logger.error(f"Error creating bot for user {user_id}: {e}")
            return None
    
    async def _create_bot_via_botfather(self, username: str, display_name: str) -> Optional[Dict[str, Any]]:
        """
        Создание бота через BotFather API
        
        Args:
            username: Имя пользователя бота
            display_name: Отображаемое имя
            
        Returns:
            Информация о боте или None при ошибке
        """
        try:
            # В реальной реализации здесь был бы вызов BotFather API
            # Для MVP используем заглушку
            logger.info(f"Creating bot {username} with display name {display_name}")
            
            # Заглушка - в реальности нужно вызывать BotFather API
            return {
                'username': username,
                'token': f"123456789:ABCdefGHIjklMNOpqrsTUVwxyz{username}",
                'display_name': display_name
            }
            
        except Exception as e:
            logger.error(f"Error creating bot via BotFather: {e}")
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
