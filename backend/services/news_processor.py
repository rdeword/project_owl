"""
Процессор новостей - обработка и сохранение новостей
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from backend.config.settings import get_settings
from backend.models.database import get_db
from backend.models.models import News, Channel, UserChannelSubscription, UserCategory, NewsCategory

settings = get_settings()
logger = logging.getLogger(__name__)


class NewsProcessor:
    """Процессор новостей"""
    
    def __init__(self):
        self.batch_size = settings.news_batch_size
        self.processing_queue = asyncio.Queue()
        self._start_processing_task()
    
    def _start_processing_task(self):
        """Запуск задачи обработки новостей"""
        asyncio.create_task(self._process_news_batch())
    
    async def process_news(self, news_data: Dict[str, Any]):
        """
        Добавление новости в очередь обработки
        
        Args:
            news_data: Данные новости
        """
        try:
            await self.processing_queue.put(news_data)
            logger.debug(f"Added news to processing queue: {news_data.get('message_id')}")
        except Exception as e:
            logger.error(f"Error adding news to queue: {e}")
    
    async def _process_news_batch(self):
        """Обработка батча новостей"""
        while True:
            try:
                # Собираем батч новостей
                batch = []
                for _ in range(self.batch_size):
                    try:
                        news_data = await asyncio.wait_for(
                            self.processing_queue.get(), 
                            timeout=1.0
                        )
                        batch.append(news_data)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    await self._process_batch(batch)
                
                # Небольшая пауза между батчами
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in news batch processing: {e}")
                await asyncio.sleep(1)
    
    async def _process_batch(self, batch: List[Dict[str, Any]]):
        """
        Обработка батча новостей
        
        Args:
            batch: Список данных новостей
        """
        try:
            async for db in get_db():
                for news_data in batch:
                    await self._save_news(db, news_data)
                    await self._categorize_news(db, news_data)
                
                await db.commit()
                logger.info(f"Processed batch of {len(batch)} news items")
                
        except Exception as e:
            logger.error(f"Error processing news batch: {e}")
    
    async def _save_news(self, db: AsyncSession, news_data: Dict[str, Any]):
        """
        Сохранение новости в базу данных
        
        Args:
            db: Сессия базы данных
            news_data: Данные новости
        """
        try:
            # Находим канал в базе данных
            channel_result = await db.execute(
                select(Channel).where(Channel.telegram_id == news_data['channel_id'])
            )
            channel = channel_result.scalar_one_or_none()
            
            if not channel:
                logger.warning(f"Channel {news_data['channel_id']} not found in database")
                return
            
            # Проверяем, не существует ли уже такая новость
            existing_news = await db.execute(
                select(News).where(
                    and_(
                        News.channel_id == channel.id,
                        News.telegram_message_id == news_data['message_id']
                    )
                )
            )
            
            if existing_news.scalar_one_or_none():
                logger.debug(f"News {news_data['message_id']} already exists")
                return
            
            # Создаем новость
            news = News(
                channel_id=channel.id,
                telegram_message_id=news_data['message_id'],
                content=news_data['content'],
                media_urls=news_data.get('media_urls', []),
                published_at=news_data['published_at']
            )
            
            db.add(news)
            await db.flush()  # Получаем ID новости
            
            logger.info(f"Saved news {news.id} from channel {channel.title}")
            
        except Exception as e:
            logger.error(f"Error saving news: {e}")
    
    async def _categorize_news(self, db: AsyncSession, news_data: Dict[str, Any]):
        """
        Категоризация новости
        
        Args:
            db: Сессия базы данных
            news_data: Данные новости
        """
        try:
            # Находим канал
            channel_result = await db.execute(
                select(Channel).where(Channel.telegram_id == news_data['channel_id'])
            )
            channel = channel_result.scalar_one_or_none()
            
            if not channel:
                return
            
            # Находим новость
            news_result = await db.execute(
                select(News).where(
                    and_(
                        News.channel_id == channel.id,
                        News.telegram_message_id == news_data['message_id']
                    )
                )
            )
            news = news_result.scalar_one_or_none()
            
            if not news:
                return
            
            # Получаем всех пользователей, подписанных на этот канал
            subscriptions_result = await db.execute(
                select(UserChannelSubscription).where(
                    UserChannelSubscription.channel_id == channel.id
                )
            )
            subscriptions = subscriptions_result.scalars().all()
            
            # Для каждого пользователя категоризируем новость
            for subscription in subscriptions:
                await self._categorize_for_user(db, news, subscription.user_id)
                
        except Exception as e:
            logger.error(f"Error categorizing news: {e}")
    
    async def _categorize_for_user(self, db: AsyncSession, news: News, user_id: int):
        """
        Категоризация новости для конкретного пользователя
        
        Args:
            db: Сессия базы данных
            news: Новость
            user_id: ID пользователя
        """
        try:
            # Получаем категории пользователя
            categories_result = await db.execute(
                select(UserCategory).where(UserCategory.user_id == user_id)
            )
            categories = categories_result.scalars().all()
            
            content_lower = news.content.lower()
            
            for category in categories:
                if not category.keywords:
                    continue
                
                # Проверяем совпадение ключевых слов
                matches = sum(1 for keyword in category.keywords if keyword.lower() in content_lower)
                
                if matches > 0:
                    # Создаем связь новости с категорией
                    news_category = NewsCategory(
                        news_id=news.id,
                        category_id=category.id,
                        confidence=min(matches / len(category.keywords), 1.0)
                    )
                    db.add(news_category)
                    
                    logger.debug(f"Categorized news {news.id} as {category.name} for user {user_id}")
                    
        except Exception as e:
            logger.error(f"Error categorizing news for user {user_id}: {e}")
    
    async def get_news_for_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        category_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Получение новостей для пользователя
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            category_id: ID категории (опционально)
            limit: Лимит новостей
            
        Returns:
            Список новостей
        """
        try:
            # Получаем каналы пользователя
            subscriptions_result = await db.execute(
                select(UserChannelSubscription).where(
                    UserChannelSubscription.user_id == user_id
                )
            )
            subscriptions = subscriptions_result.scalars().all()
            
            if not subscriptions:
                return []
            
            channel_ids = [sub.channel_id for sub in subscriptions]
            
            # Базовый запрос
            query = select(News).where(News.channel_id.in_(channel_ids))
            
            if category_id:
                # Фильтр по категории
                query = query.join(NewsCategory).where(
                    NewsCategory.category_id == category_id
                )
            
            query = query.order_by(News.published_at.desc()).limit(limit)
            
            result = await db.execute(query)
            news_items = result.scalars().all()
            
            # Формируем результат
            news_list = []
            for news in news_items:
                news_dict = {
                    'id': news.id,
                    'content': news.content,
                    'media_urls': news.media_urls or [],
                    'published_at': news.published_at.isoformat(),
                    'channel_title': news.channel.title,
                    'categories': []
                }
                
                # Получаем категории новости
                categories_result = await db.execute(
                    select(NewsCategory, UserCategory).join(
                        UserCategory, NewsCategory.category_id == UserCategory.id
                    ).where(NewsCategory.news_id == news.id)
                )
                
                for news_cat, category in categories_result:
                    news_dict['categories'].append({
                        'name': category.name,
                        'color': category.color,
                        'confidence': news_cat.confidence
                    })
                
                news_list.append(news_dict)
            
            return news_list
            
        except Exception as e:
            logger.error(f"Error getting news for user {user_id}: {e}")
            return []
