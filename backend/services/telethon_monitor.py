"""
Telethon монитор для получения новостей в реальном времени
"""
import asyncio
import logging
from typing import Set, Dict, Any, Optional
from telethon import TelegramClient, events
from telethon.tl.types import Channel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.settings import get_settings
from backend.models.database import get_db
from backend.models.models import Channel as ChannelModel, News, UserChannelSubscription
from backend.services.news_processor import NewsProcessor

settings = get_settings()
logger = logging.getLogger(__name__)


class TelethonMonitor:
    """Монитор каналов через Telethon"""
    
    def __init__(self):
        self.client = TelegramClient(
            'news_monitor',
            settings.telegram_api_id,
            settings.telegram_api_hash
        )
        self.monitored_channels: Set[int] = set()
        self.news_processor = NewsProcessor()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков событий"""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            """Обработка новых сообщений"""
            try:
                # Проверяем, что это канал из нашего списка
                if event.chat_id in self.monitored_channels:
                    await self.process_new_message(event)
            except Exception as e:
                logger.error(f"Error handling new message: {e}")
    
    async def start(self):
        """Запуск мониторинга каналов"""
        try:
            await self.client.start()
            logger.info("Telethon monitor started")
            
            # Загружаем каналы из базы данных
            await self.load_monitored_channels()
            
        except Exception as e:
            logger.error(f"Error starting Telethon monitor: {e}")
            raise
    
    async def stop(self):
        """Остановка мониторинга"""
        try:
            await self.client.disconnect()
            logger.info("Telethon monitor stopped")
        except Exception as e:
            logger.error(f"Error stopping Telethon monitor: {e}")
    
    async def load_monitored_channels(self):
        """Загрузка каналов для мониторинга из базы данных"""
        try:
            async for db in get_db():
                # Получаем все активные каналы
                from sqlalchemy import select
                result = await db.execute(
                    select(ChannelModel.telegram_id).where(ChannelModel.is_active == True)
                )
                channel_ids = result.scalars().all()
                
                self.monitored_channels.update(channel_ids)
                logger.info(f"Loaded {len(channel_ids)} channels for monitoring")
                
        except Exception as e:
            logger.error(f"Error loading monitored channels: {e}")
    
    async def add_channel(self, channel_username: str, user_id: int) -> bool:
        """
        Добавление канала для мониторинга
        
        Args:
            channel_username: Имя канала (@channel_name)
            user_id: ID пользователя
            
        Returns:
            True если успешно, False иначе
        """
        try:
            # Получаем информацию о канале
            channel = await self.client.get_entity(channel_username)
            
            if not isinstance(channel, Channel):
                logger.error(f"Entity {channel_username} is not a channel")
                return False
            
            # Сохраняем канал в базу данных
            async for db in get_db():
                # Проверяем, существует ли канал
                from sqlalchemy import select
                result = await db.execute(
                    select(ChannelModel).where(ChannelModel.telegram_id == channel.id)
                )
                channel_model = result.scalar_one_or_none()
                
                if not channel_model:
                    # Создаем новый канал
                    channel_model = ChannelModel(
                        telegram_id=channel.id,
                        username=channel.username,
                        title=channel.title,
                        description=getattr(channel, 'about', None),
                        subscribers_count=getattr(channel, 'participants_count', None)
                    )
                    db.add(channel_model)
                    await db.commit()
                    await db.refresh(channel_model)
                
                # Создаем подписку пользователя на канал
                from backend.models.models import UserChannelSubscription, UserBot
                
                # Получаем бота пользователя
                bot_result = await db.execute(
                    select(UserBot).where(
                        UserBot.user_id == user_id,
                        UserBot.is_active == True
                    )
                )
                user_bot = bot_result.scalar_one_or_none()
                
                if not user_bot:
                    logger.error(f"No active bot found for user {user_id}")
                    return False
                
                # Создаем подписку
                subscription = UserChannelSubscription(
                    user_id=user_id,
                    channel_id=channel_model.id,
                    bot_id=user_bot.id
                )
                db.add(subscription)
                await db.commit()
                
                # Добавляем в список мониторинга
                self.monitored_channels.add(channel.id)
                
                logger.info(f"Added channel {channel_username} for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding channel {channel_username}: {e}")
            return False
    
    async def remove_channel(self, channel_username: str, user_id: int) -> bool:
        """
        Удаление канала из мониторинга
        
        Args:
            channel_username: Имя канала
            user_id: ID пользователя
            
        Returns:
            True если успешно, False иначе
        """
        try:
            # Получаем информацию о канале
            channel = await self.client.get_entity(channel_username)
            
            # Удаляем подписку из базы данных
            async for db in get_db():
                from sqlalchemy import select, delete
                
                # Находим канал
                channel_result = await db.execute(
                    select(ChannelModel).where(ChannelModel.telegram_id == channel.id)
                )
                channel_model = channel_result.scalar_one_or_none()
                
                if channel_model:
                    # Удаляем подписку
                    await db.execute(
                        delete(UserChannelSubscription).where(
                            UserChannelSubscription.user_id == user_id,
                            UserChannelSubscription.channel_id == channel_model.id
                        )
                    )
                    await db.commit()
                
                # Удаляем из списка мониторинга
                self.monitored_channels.discard(channel.id)
                
                logger.info(f"Removed channel {channel_username} for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error removing channel {channel_username}: {e}")
            return False
    
    async def process_new_message(self, event):
        """Обработка нового сообщения из канала"""
        try:
            message = event.message
            
            # Извлекаем данные сообщения
            news_data = {
                'channel_id': event.chat_id,
                'message_id': message.id,
                'content': message.text or '',
                'media_urls': self.extract_media_urls(message),
                'published_at': message.date,
                'raw_message': message
            }
            
            # Отправляем на обработку
            await self.news_processor.process_news(news_data)
            
            logger.info(f"Processed new message from channel {event.chat_id}")
            
        except Exception as e:
            logger.error(f"Error processing new message: {e}")
    
    def extract_media_urls(self, message) -> list[str]:
        """Извлечение URL медиафайлов из сообщения"""
        urls = []
        
        try:
            if message.photo:
                urls.append(f"photo_{message.photo.id}")
            if message.video:
                urls.append(f"video_{message.video.id}")
            if message.document:
                urls.append(f"document_{message.document.id}")
            if message.audio:
                urls.append(f"audio_{message.audio.id}")
            if message.voice:
                urls.append(f"voice_{message.voice.id}")
        except Exception as e:
            logger.error(f"Error extracting media URLs: {e}")
        
        return urls
    
    async def run_forever(self):
        """Запуск мониторинга навсегда"""
        try:
            await self.client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Error in run_forever: {e}")
            raise


# Создаем глобальный экземпляр монитора
telethon_monitor = TelethonMonitor()
