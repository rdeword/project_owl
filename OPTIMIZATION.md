# 🚀 Оптимизация проекта с учетом ограничений Telegram API

## ⚠️ Критические ограничения Telegram API

### **1. Ограничения Bot API**
- **30 сообщений в секунду** для всех пользователей
- **20 запросов в секунду** на каждый метод API
- **50 МБ** максимальный размер файла
- **100 кнопок** максимум в одном сообщении
- **256 символов** максимум для команд

### **2. Ограничения BotFather**
- **❌ НЕТ API** для автоматического создания ботов
- **❌ НЕТ API** для программного управления ботами
- **✅ ТОЛЬКО РУЧНОЕ** создание через интерфейс BotFather

### **3. Ограничения Telethon**
- **Rate limits** при мониторинге множества каналов
- **Ограничения на количество** одновременно мониторимых каналов
- **Необходимость авторизации** пользователя (api_id, api_hash)

## 🔧 Решения и оптимизации

### **1. Система пула ботов**

#### **Проблема:**
BotFather не предоставляет API для автоматического создания ботов.

#### **Решение:**
```python
class BotPool:
    def __init__(self):
        self.available_bots = []  # Предварительно созданные боты
        self.assigned_bots = {}   # Пользователь -> Бот
        self.bot_tokens = self.load_bot_tokens_from_env()
    
    def load_bot_tokens_from_env(self):
        """Загрузка токенов ботов из переменных окружения"""
        tokens = []
        for i in range(1, 501):  # 500 ботов в пуле
            token = os.getenv(f"BOT_POOL_TOKEN_{i}")
            if token:
                tokens.append({
                    'token': token,
                    'username': f"userbot_{i}",
                    'is_available': True
                })
        return tokens
    
    async def assign_bot_to_user(self, user_id: int):
        """Назначение бота пользователю"""
        for bot in self.bot_tokens:
            if bot['is_available']:
                bot['is_available'] = False
                bot['assigned_to'] = user_id
                return bot
        return None  # Нет свободных ботов
```

### **2. Rate Limiting для сообщений**

#### **Проблема:**
Ограничение 30 сообщений в секунду для всех пользователей.

#### **Решение:**
```python
import asyncio
from collections import deque
import time

class RateLimiter:
    def __init__(self, max_requests: int = 30, time_window: int = 1):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.semaphore = asyncio.Semaphore(max_requests)
    
    async def acquire(self):
        """Получение разрешения на отправку сообщения"""
        await self.semaphore.acquire()
        now = time.time()
        
        # Удаляем старые запросы
        while self.requests and self.requests[0] <= now - self.time_window:
            self.requests.popleft()
        
        if len(self.requests) >= self.max_requests:
            # Ждем, пока освободится место
            sleep_time = self.requests[0] + self.time_window - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.requests.append(now)
        self.semaphore.release()

class MessageQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.rate_limiter = RateLimiter(30)  # 30 сообщений в секунду
        self.worker_task = None
    
    async def start_worker(self):
        """Запуск воркера для обработки очереди сообщений"""
        while True:
            try:
                user_id, message = await self.queue.get()
                await self.rate_limiter.acquire()
                await self.send_message_to_user(user_id, message)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def add_message(self, user_id: int, message: str):
        """Добавление сообщения в очередь"""
        await self.queue.put((user_id, message))
```

### **3. Оптимизация Telethon мониторинга**

#### **Проблема:**
Rate limits при мониторинге множества каналов.

#### **Решение:**
```python
class OptimizedChannelMonitor:
    def __init__(self):
        self.user_channels = {}  # user_id -> [channels]
        self.channel_users = {}  # channel_id -> [user_ids]
        self.rate_limiter = RateLimiter(20)  # 20 запросов в секунду
    
    async def add_channel_for_user(self, user_id: int, channel: str):
        """Добавление канала для мониторинга с оптимизацией"""
        channel_id = await self.get_channel_id(channel)
        
        # Если канал уже мониторится, просто добавляем пользователя
        if channel_id in self.channel_users:
            if user_id not in self.channel_users[channel_id]:
                self.channel_users[channel_id].append(user_id)
        else:
            # Новый канал - добавляем в мониторинг
            self.channel_users[channel_id] = [user_id]
            await self.start_monitoring_channel(channel_id)
        
        # Обновляем список каналов пользователя
        if user_id not in self.user_channels:
            self.user_channels[user_id] = []
        if channel_id not in self.user_channels[user_id]:
            self.user_channels[user_id].append(channel_id)
    
    async def process_new_message(self, event, channel_id: int):
        """Обработка нового сообщения с батчевой отправкой"""
        user_ids = self.channel_users.get(channel_id, [])
        
        # Группируем пользователей для батчевой отправки
        for user_id in user_ids:
            await self.rate_limiter.acquire()
            await self.send_to_user_batch(user_id, event.message)
```

### **4. Оптимизация Inline Keyboard**

#### **Проблема:**
Максимум 100 кнопок в одном сообщении.

#### **Решение:**
```python
class PaginatedKeyboard:
    def __init__(self, max_buttons_per_page: int = 100):
        self.max_buttons = max_buttons_per_page
    
    def create_paginated_menu(self, items: list, page: int = 0, prefix: str = ""):
        """Создание пагинированного меню"""
        start = page * self.max_buttons
        end = start + self.max_buttons
        page_items = items[start:end]
        
        keyboard = []
        for item in page_items:
            keyboard.append([InlineKeyboardButton(
                text=item['text'],
                callback_data=f"{prefix}_{item['id']}"
            )])
        
        # Добавляем кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"{prefix}_page_{page-1}"
            ))
        if end < len(items):
            nav_buttons.append(InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"{prefix}_page_{page+1}"
            ))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
```

### **5. Кэширование для снижения нагрузки**

#### **Решение:**
```python
import redis
import json
from typing import Optional, Any

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 час
    
    async def get(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Сохранение данных в кэш"""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def get_news_for_user(self, user_id: int, category: str = None):
        """Получение новостей для пользователя с кэшированием"""
        cache_key = f"news_user_{user_id}_{category or 'all'}"
        cached_news = await self.get(cache_key)
        
        if cached_news:
            return cached_news
        
        # Получаем новости из базы данных
        news = await self.fetch_news_from_db(user_id, category)
        
        # Кэшируем на 5 минут
        await self.set(cache_key, news, 300)
        return news
```

### **6. Батчевая обработка ИИ запросов**

#### **Решение:**
```python
class AIBatchProcessor:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.batch_size = 10  # Обрабатываем по 10 новостей за раз
        self.rate_limiter = RateLimiter(60)  # 60 запросов в минуту для OpenAI
    
    async def process_news_batch(self, news_items: list):
        """Батчевая обработка новостей для категоризации"""
        batches = [news_items[i:i+self.batch_size] 
                  for i in range(0, len(news_items), self.batch_size)]
        
        results = []
        for batch in batches:
            await self.rate_limiter.acquire()
            
            # Объединяем новости в один запрос
            combined_text = "\n\n".join([item['content'] for item in batch])
            
            # Отправляем один запрос для всей пачки
            categories = await self.categorize_text(combined_text)
            
            # Распределяем результаты по новостям
            for i, item in enumerate(batch):
                item['category'] = categories[i] if i < len(categories) else 'other'
                results.append(item)
        
        return results
    
    async def categorize_text(self, text: str):
        """Категоризация текста через OpenAI API"""
        # Реализация запроса к OpenAI API
        pass
```

## 📊 Мониторинг производительности

### **Метрики для отслеживания:**
- **Rate limit violations** - превышения лимитов API
- **Queue length** - длина очереди сообщений
- **Cache hit rate** - эффективность кэширования
- **Response time** - время отклика системы
- **Bot pool utilization** - использование пула ботов

### **Алерты:**
- Превышение 80% лимитов API
- Очередь сообщений > 1000 элементов
- Кэш hit rate < 70%
- Время отклика > 5 секунд
- Свободных ботов < 10%

## 🎯 Итоговые рекомендации

### **1. Обязательные оптимизации:**
- ✅ **Rate limiting** для всех API вызовов
- ✅ **Очереди сообщений** для соблюдения лимитов
- ✅ **Кэширование** для снижения нагрузки
- ✅ **Пул ботов** вместо автоматического создания
- ✅ **Батчевая обработка** для ИИ запросов

### **2. Дополнительные оптимизации:**
- 🔄 **Пагинация** для больших списков
- 🔄 **Ленивая загрузка** для Web App
- 🔄 **Сжатие данных** для передачи
- 🔄 **CDN** для статических файлов
- 🔄 **Горизонтальное масштабирование** при росте нагрузки

### **3. Мониторинг и алерты:**
- 📊 **Метрики производительности**
- 🚨 **Автоматические алерты**
- 📈 **Графики нагрузки**
- 🔍 **Логирование ошибок**

С этими оптимизациями проект будет работать стабильно в рамках ограничений Telegram API! 🚀
