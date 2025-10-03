"""
Модели базы данных
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey, 
    Integer, String, Text, ARRAY, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.models.database import Base


class User(Base):
    """Пользователи системы"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    username = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Связи
    bots = relationship("UserBot", back_populates="user", cascade="all, delete-orphan")
    channel_subscriptions = relationship("UserChannelSubscription", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("UserCategory", back_populates="user", cascade="all, delete-orphan")
    ai_summaries = relationship("AISummary", back_populates="user", cascade="all, delete-orphan")


class UserBot(Base):
    """Боты пользователей"""
    __tablename__ = "user_bots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bot_token = Column(String(255), unique=True, nullable=False)
    bot_username = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="bots")
    channel_subscriptions = relationship("UserChannelSubscription", back_populates="bot", cascade="all, delete-orphan")


class Channel(Base):
    """Каналы для мониторинга"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subscribers_count = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    subscriptions = relationship("UserChannelSubscription", back_populates="channel", cascade="all, delete-orphan")
    news = relationship("News", back_populates="channel", cascade="all, delete-orphan")


class UserChannelSubscription(Base):
    """Подписки пользователей на каналы"""
    __tablename__ = "user_channel_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    bot_id = Column(Integer, ForeignKey("user_bots.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Уникальность подписки
    __table_args__ = (
        UniqueConstraint('user_id', 'channel_id', name='unique_user_channel'),
    )
    
    # Связи
    user = relationship("User", back_populates="channel_subscriptions")
    channel = relationship("Channel", back_populates="subscriptions")
    bot = relationship("UserBot", back_populates="channel_subscriptions")


class UserCategory(Base):
    """Категории пользователей"""
    __tablename__ = "user_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=True)  # HEX цвет
    keywords = Column(ARRAY(String), nullable=True)  # Массив ключевых слов
    is_auto = Column(Boolean, default=False)  # Автоматическая категоризация
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="categories")
    news_categories = relationship("NewsCategory", back_populates="category", cascade="all, delete-orphan")


class News(Base):
    """Новости"""
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    telegram_message_id = Column(BigInteger, nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(ARRAY(String), nullable=True)  # Массив URL медиафайлов
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    channel = relationship("Channel", back_populates="news")
    categories = relationship("NewsCategory", back_populates="news", cascade="all, delete-orphan")


class NewsCategory(Base):
    """Категоризация новостей"""
    __tablename__ = "news_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("user_categories.id"), nullable=False)
    confidence = Column(Float, nullable=True)  # Уверенность ИИ в категоризации
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    news = relationship("News", back_populates="categories")
    category = relationship("UserCategory", back_populates="news_categories")


class AISummary(Base):
    """ИИ саммари"""
    __tablename__ = "ai_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    categories = Column(ARRAY(String), nullable=True)  # Категории, по которым создано саммари
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="ai_summaries")
