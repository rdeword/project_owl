"""
Главный бот для регистрации пользователей
"""
import asyncio
import logging
from typing import Dict, Any
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from backend.config.settings import get_settings
from backend.models.database import get_db
from backend.services.bot_manager import BotManager
from backend.services.user_service import UserService

settings = get_settings()
logger = logging.getLogger(__name__)


class RegistrationStates(StatesGroup):
    """Состояния регистрации"""
    waiting_for_email = State()
    waiting_for_name = State()


class MainBot:
    """Главный бот для регистрации"""
    
    def __init__(self):
        self.bot = Bot(token=settings.main_bot_token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.bot_manager = BotManager()
        self.user_service = UserService()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков"""
        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.register_command, Command("register"))
        self.dp.message.register(self.help_command, Command("help"))
        self.dp.message.register(self.status_command, Command("status"))
        
        # FSM обработчики
        self.dp.message.register(self.process_email, RegistrationStates.waiting_for_email)
        self.dp.message.register(self.process_name, RegistrationStates.waiting_for_name)
    
    async def start_command(self, message: types.Message):
        """Обработка команды /start"""
        welcome_text = """
👋 Привет! Я помогу тебе создать персонального бота для агрегации новостей.

📰 Что я умею:
• Создавать личного бота для каждого пользователя
• Подписываться на новостные каналы
• Категоризировать новости с помощью ИИ
• Создавать саммари по выбранным темам

🚀 Чтобы начать, отправь /register
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Зарегистрироваться", callback_data="register")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
            [InlineKeyboardButton(text="📊 Статус", callback_data="status")]
        ])
        
        await message.answer(welcome_text, reply_markup=keyboard)
    
    async def register_command(self, message: types.Message, state: FSMContext):
        """Обработка команды /register"""
        # Проверяем, не зарегистрирован ли уже пользователь
        async for db in get_db():
            existing_user = await self.user_service.get_user_by_telegram_id(
                db, message.from_user.id
            )
            if existing_user:
                await message.answer(
                    "✅ Вы уже зарегистрированы! "
                    "Используйте /help для получения списка команд."
                )
                return
        
        await message.answer(
            "📝 Регистрация нового пользователя\n\n"
            "Введи свой email:"
        )
        await state.set_state(RegistrationStates.waiting_for_email)
    
    async def process_email(self, message: types.Message, state: FSMContext):
        """Обработка ввода email"""
        email = message.text.strip()
        
        # Простая валидация email
        if "@" not in email or "." not in email.split("@")[1]:
            await message.answer("❌ Неверный формат email. Попробуйте еще раз:")
            return
        
        await state.update_data(email=email)
        await message.answer("Введи свое имя:")
        await state.set_state(RegistrationStates.waiting_for_name)
    
    async def process_name(self, message: types.Message, state: FSMContext):
        """Обработка ввода имени"""
        name = message.text.strip()
        data = await state.get_data()
        email = data.get("email")
        
        await message.answer("✅ Регистрация завершена!\n\n🤖 Создаю твоего личного бота...\n⏳ Пожалуйста, подожди 30 секунд...")
        
        try:
            # Создаем пользователя в базе данных
            async for db in get_db():
                user = await self.user_service.create_user(
                    db=db,
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    email=email,
                    first_name=name
                )
                
                # Создаем личного бота
                bot_info = await self.bot_manager.create_user_bot(
                    user_id=user.id,
                    user_name=name
                )
                
                if bot_info:
                    success_text = f"""
✅ Готово! Твой личный бот: @{bot_info['username']}
🔗 Ссылка: https://t.me/{bot_info['username']}

📋 Что дальше:
1. Перейди к своему боту
2. Отправь /start
3. Добавь каналы командой /add_channel @channel_name
4. Создай категории командой /categories

Удачи! 🚀
                    """
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="🌐 Web App", 
                            web_app=WebAppInfo(url=f"{settings.webapp_url}?user_id={user.id}")
                        )]
                    ])
                    
                    await message.answer(success_text, reply_markup=keyboard)
                else:
                    await message.answer("❌ Ошибка при создании бота. Попробуйте позже.")
        
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            await message.answer("❌ Произошла ошибка при регистрации. Попробуйте позже.")
        
        finally:
            await state.clear()
    
    async def help_command(self, message: types.Message):
        """Обработка команды /help"""
        help_text = """
❓ Доступные команды:

/start - Начать работу с ботом
/register - Зарегистрироваться в системе
/help - Показать это сообщение
/status - Статус системы

📞 Поддержка: @your_support_bot
        """
        await message.answer(help_text)
    
    async def status_command(self, message: types.Message):
        """Обработка команды /status"""
        try:
            async for db in get_db():
                stats = await self.user_service.get_system_stats(db)
                
                status_text = f"""
📊 Статус системы:

👥 Пользователей: {stats.get('users_count', 0)}
🤖 Активных ботов: {stats.get('bots_count', 0)}
📰 Новостей сегодня: {stats.get('news_today', 0)}
📂 Каналов: {stats.get('channels_count', 0)}

🟢 Система работает нормально
                """
                await message.answer(status_text)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            await message.answer("❌ Ошибка при получении статуса")
    
    async def start_polling(self):
        """Запуск бота"""
        try:
            logger.info("Starting main bot...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error starting main bot: {e}")
            raise


# Создаем экземпляр бота
main_bot = MainBot()
