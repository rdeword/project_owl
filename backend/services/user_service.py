"""
Сервис для работы с пользователями
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from backend.models.models import User, UserBot, Channel, News

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями"""
    
    async def create_user(
        self,
        db: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Создание нового пользователя
        
        Args:
            db: Сессия базы данных
            telegram_id: Telegram ID пользователя
            username: Имя пользователя
            email: Email
            first_name: Имя
            last_name: Фамилия
            
        Returns:
            Созданный пользователь
        """
        user = User(
            telegram_id=telegram_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Created user {user.id} with telegram_id {telegram_id}")
        return user
    
    async def get_user_by_telegram_id(self, db: AsyncSession, telegram_id: int) -> Optional[User]:
        """
        Получение пользователя по Telegram ID
        
        Args:
            db: Сессия базы данных
            telegram_id: Telegram ID
            
        Returns:
            Пользователь или None
        """
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            
        Returns:
            Пользователь или None
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_bot(self, db: AsyncSession, user_id: int) -> Optional[UserBot]:
        """
        Получение бота пользователя
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            
        Returns:
            Бот пользователя или None
        """
        result = await db.execute(
            select(UserBot).where(
                and_(UserBot.user_id == user_id, UserBot.is_active == True)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_active_bots(self, db: AsyncSession) -> list[UserBot]:
        """
        Получение всех активных ботов
        
        Args:
            db: Сессия базы данных
            
        Returns:
            Список активных ботов
        """
        result = await db.execute(
            select(UserBot).where(UserBot.is_active == True)
        )
        return result.scalars().all()
    
    async def get_system_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Получение статистики системы
        
        Args:
            db: Сессия базы данных
            
        Returns:
            Словарь со статистикой
        """
        try:
            # Количество пользователей
            users_count = await db.scalar(select(func.count(User.id)))
            
            # Количество активных ботов
            bots_count = await db.scalar(
                select(func.count(UserBot.id)).where(UserBot.is_active == True)
            )
            
            # Количество каналов
            channels_count = await db.scalar(
                select(func.count(Channel.id)).where(Channel.is_active == True)
            )
            
            # Количество новостей за сегодня
            today = datetime.utcnow().date()
            news_today = await db.scalar(
                select(func.count(News.id)).where(
                    func.date(News.created_at) == today
                )
            )
            
            return {
                'users_count': users_count or 0,
                'bots_count': bots_count or 0,
                'channels_count': channels_count or 0,
                'news_today': news_today or 0
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {
                'users_count': 0,
                'bots_count': 0,
                'channels_count': 0,
                'news_today': 0
            }
    
    async def update_user(self, db: AsyncSession, user_id: int, **kwargs) -> Optional[User]:
        """
        Обновление пользователя
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            **kwargs: Поля для обновления
            
        Returns:
            Обновленный пользователь или None
        """
        try:
            user = await self.get_user_by_id(db, user_id)
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Updated user {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    async def deactivate_user(self, db: AsyncSession, user_id: int) -> bool:
        """
        Деактивация пользователя
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            
        Returns:
            True если успешно, False иначе
        """
        try:
            user = await self.get_user_by_id(db, user_id)
            if not user:
                return False
            
            user.is_active = False
            await db.commit()
            
            logger.info(f"Deactivated user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False
