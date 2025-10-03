"""
Тесты для UserService
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.user_service import UserService
from backend.models.models import User


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Тест создания пользователя"""
    user_service = UserService()
    
    user = await user_service.create_user(
        db=db_session,
        telegram_id=123456789,
        username="test_user",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    
    assert user.id is not None
    assert user.telegram_id == 123456789
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"


@pytest.mark.asyncio
async def test_get_user_by_telegram_id(db_session: AsyncSession):
    """Тест получения пользователя по Telegram ID"""
    user_service = UserService()
    
    # Создаем пользователя
    user = await user_service.create_user(
        db=db_session,
        telegram_id=123456789,
        username="test_user"
    )
    
    # Получаем пользователя
    found_user = await user_service.get_user_by_telegram_id(
        db=db_session,
        telegram_id=123456789
    )
    
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.telegram_id == 123456789


@pytest.mark.asyncio
async def test_get_system_stats(db_session: AsyncSession):
    """Тест получения статистики системы"""
    user_service = UserService()
    
    # Создаем тестовых пользователей
    await user_service.create_user(
        db=db_session,
        telegram_id=111111111,
        username="user1"
    )
    await user_service.create_user(
        db=db_session,
        telegram_id=222222222,
        username="user2"
    )
    
    # Получаем статистику
    stats = await user_service.get_system_stats(db_session)
    
    assert stats['users_count'] >= 2
    assert 'bots_count' in stats
    assert 'channels_count' in stats
    assert 'news_today' in stats
