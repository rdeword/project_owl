# 📰 Telegram News Aggregator - Техническое описание

## 🎯 Описание проекта

Telegram-агрегатор новостей - это система, которая автоматически подписывается на указанные новостные каналы и предоставляет пользователю удобный интерфейс для просмотра, категоризации и анализа новостей с возможностью создания саммари и персонализированных дайджестов.

## 🏗️ Упрощенная архитектура системы

### Принцип: Только Telegram + Встроенные интерфейсы

**Основная идея:** Все взаимодействие происходит через Telegram-ботов с использованием встроенных интерфейсов (Inline Keyboard, Web App, Inline Query).

### Архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM LAYER                               │
├─────────────────┬───────────────────────────────────────────────┤
│   Главный бот   │              Личные боты                      │
│ @NewsAggregator │  @UserBot1  @UserBot2  ...  @UserBotN        │
│   (Регистрация) │    (Пользователь 1)  (Пользователь 2)        │
└─────────────────┴───────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────────┐
│                    CORE SERVICES                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   News      │  │     AI      │  │    Bot Manager          │ │
│  │ Aggregator  │  │  Services   │  │   (Multi-Bot)           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Channel    │  │  Category   │  │    User Management      │ │
│  │  Manager    │  │  Manager    │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              TELETHON MONITOR                               │ │
│  │         (Real-time Channel Monitoring)                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ PostgreSQL  │  │    Redis    │  │    File Storage         │ │
│  │  Database   │  │   Cache     │  │   (Media Files)         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Встроенные интерфейсы Telegram

#### 1. **Inline Keyboard (Встроенная клавиатура)**
- **Меню навигации** - кнопки для основных функций
- **Выбор категорий** - кнопки для фильтрации новостей
- **Управление каналами** - добавление/удаление каналов
- **Настройки** - конфигурация уведомлений и категорий

#### 2. **Web App (Встроенное веб-приложение)**
- **Расширенное управление** - сложные формы и таблицы
- **Аналитика** - графики и статистика
- **Настройка категорий** - детальная конфигурация
- **Поиск и фильтры** - продвинутый поиск новостей

#### 3. **Inline Query (Встроенный поиск)**
- **Быстрый поиск** - поиск новостей через @бот
- **Автодополнение** - предложения при вводе
- **Превью новостей** - предварительный просмотр

#### 4. **Callback Query (Обработка нажатий)**
- **Интерактивность** - реакция на нажатия кнопок
- **Состояния** - запоминание действий пользователя
- **Пейджинация** - навигация по страницам

### Система ботов

#### 1. **Главный бот (@NewsAggregatorBot)**
- **Назначение:** Регистрация новых пользователей и создание личных ботов
- **Функции:**
  - `/start` - приветствие и инструкции
  - `/register` - регистрация нового пользователя
  - `/help` - помощь и поддержка
  - `/status` - статус системы
- **Процесс регистрации:**
  1. Пользователь отправляет `/register`
  2. Бот запрашивает email и имя
  3. Система назначает бота из пула предварительно созданных ботов
  4. Пользователь получает ссылку на назначенного бота

#### 2. **Личные боты (@UserBot123, @UserBot456, ...)**
- **Назначение:** Персональный бот каждого пользователя
- **Функции:**
  - `/start` - начало работы с ботом
  - `/add_channel @channel` - добавить канал
  - `/remove_channel @channel` - удалить канал
  - `/list_channels` - показать все каналы
  - `/categories` - управление категориями
  - `/news` - получить новости
  - `/news politics` - новости по категории
  - `/summary` - получить саммари
  - `/search "ключевые слова"` - поиск новостей
  - `/settings` - настройки уведомлений

#### 3. **Bot Pool (Пул ботов)**
- **Назначение:** Хранение и управление предварительно созданными ботами
- **Количество:** Предварительно созданные боты (100-500 ботов в пуле)
- **Управление:** Назначение/освобождение ботов из пула
- **Мониторинг:** Отслеживание состояния и активности ботов

#### 4. **Bot Manager (Менеджер ботов)**
- **Пул ботов:** Использование предварительно созданных ботов (100-500 ботов)
- **Назначение ботов:** Автоматическое назначение бота из пула пользователю
- **Мониторинг:** Отслеживание состояния и активности ботов
- **Масштабирование:** Добавление новых ботов в пул при необходимости
- **Очистка:** Освобождение неактивных ботов обратно в пул

#### 5. **User Management (Управление пользователями)**
- **Регистрация:** Создание аккаунта через Telegram + выделение бота
- **Аутентификация:** 
  - Telegram-аутентификация для ботов
  - JWT токены для веб-интерфейса
- **Профили:** Настройки пользователя и его ботов
- **Связи:** Привязка пользователя к его личному боту

#### 6. **Telethon Monitor (Мониторинг каналов)**
- **Назначение:** Мгновенное получение новых сообщений из каналов
- **Принцип работы:** 
  - Telethon работает как пользовательский клиент
  - Подписывается на обновления всех каналов пользователей
  - Получает сообщения в реальном времени через webhook
  - **Оптимизация:** Группировка каналов по пользователям для снижения нагрузки
- **Преимущества:**
  - **Мгновенность** - сообщения приходят сразу после публикации
  - **Эффективность** - не нужно постоянно опрашивать API
  - **Масштабируемость** - один клиент может мониторить множество каналов
- **Ограничения и решения:**
  - Требует авторизации пользователя (api_id, api_hash)
  - Работает от имени пользователя, а не бота
  - **Rate limiting:** Соблюдение лимитов 30 сообщений/сек
  - **Очереди:** Батчевая обработка сообщений для оптимизации

## 🔄 Детальный механизм работы системы

### 1. **Регистрация пользователя через Telegram**

#### Вариант A: Через главного бота (Рекомендуемый)
```
Пользователь → Главный бот → Регистрация → Создание личного бота → Готов к работе
     ↓              ↓           ↓              ↓                    ↓
1. /start → 2. /register → 3. Вводит данные → 4. Система создает → 5. Получает доступ
```

**Процесс:**
1. Пользователь находит главного бота (например, @NewsAggregatorBot)
2. Отправляет `/start` → получает приветствие и инструкции
3. Отправляет `/register` → система запрашивает данные (email, имя)
4. Система назначает бота из пула предварительно созданных ботов
5. Пользователь получает ссылку на назначенного бота
6. Бот помечается как занятый в пуле ботов системы

#### Вариант B: Прямая регистрация через личного бота
```
Пользователь → Личный бот → Первый запуск → Регистрация → Настройка
     ↓              ↓           ↓              ↓            ↓
1. Переходит по ссылке → 2. /start → 3. Вводит данные → 4. Сохраняется → 5. Готов
```

**Процесс:**
1. Пользователь получает ссылку на личного бота (например, @User123NewsBot)
2. Отправляет `/start` → бот проверяет, зарегистрирован ли пользователь
3. Если нет → запрашивает данные для регистрации
4. Данные сохраняются в базу данных
5. Пользователь получает доступ к функциям бота

#### Преимущества Telegram-регистрации:
- **Быстрота** - не нужно переходить на сайт
- **Удобство** - все в одном приложении
- **Безопасность** - аутентификация через Telegram
- **Мобильность** - работает на всех устройствах

#### Пример диалога с главным ботом:
```
Пользователь: /start
@NewsAggregatorBot: 👋 Привет! Я помогу тебе создать персонального бота для агрегации новостей.

📰 Что я умею:
• Создавать личного бота для каждого пользователя
• Подписываться на новостные каналы
• Категоризировать новости с помощью ИИ
• Создавать саммари по выбранным темам

🚀 Чтобы начать, отправь /register

Пользователь: /register
@NewsAggregatorBot: 📝 Регистрация нового пользователя

Введи свой email:
Пользователь: user@example.com
@NewsAggregatorBot: Введи свое имя:
Пользователь: Иван
@NewsAggregatorBot: ✅ Регистрация завершена!

🤖 Назначаю тебе персонального бота...
⏳ Пожалуйста, подожди 5 секунд...

✅ Готово! Твой персональный бот: @IvanNewsBot123
🔗 Ссылка: https://t.me/IvanNewsBot123

📋 Что дальше:
1. Перейди к своему боту
2. Отправь /start
3. Добавь каналы командой /add_channel @channel_name
4. Создай категории командой /categories

Удачи! 🚀
```

#### Пример диалога с личным ботом:
```
Пользователь: /start
@IvanNewsBot123: 👋 Привет, Иван! Я твой персональный агрегатор новостей.

📊 Твоя статистика:
• Каналов: 0
• Категорий: 0
• Новостей: 0

🚀 Начни с добавления каналов:
/add_channel @channel_name

Пользователь: /add_channel @meduzaproject
@IvanNewsBot123: ✅ Канал @meduzaproject добавлен!

📊 Обновленная статистика:
• Каналов: 1
• Категорий: 0
• Новостей: 0

Пользователь: /add_channel @tass_agency
@IvanNewsBot123: ✅ Канал @tass_agency добавлен!

Пользователь: /categories
@IvanNewsBot123: 📂 Управление категориями

Создать новую категорию:
/create_category

Список категорий:
• Пока нет категорий

Пользователь: /create_category
@IvanNewsBot123: 📝 Создание новой категории

Введи название категории:
Пользователь: Политика
@IvanNewsBot123: Введи ключевые слова через запятую:
Пользователь: выборы, президент, правительство, парламент
@IvanNewsBot123: ✅ Категория "Политика" создана!

Пользователь: /news
@IvanNewsBot123: 📰 Последние новости

🏛️ Политика (2 новости):
• [15:30] @meduzaproject: Президент подписал новый закон...
• [14:45] @tass_agency: Министр экономики выступил с заявлением...

💰 Другие новости (3 новости):
• [16:20] @meduzaproject: Рубль укрепился на 2%...
• [15:10] @tass_agency: Инфляция замедлилась...

Пользователь: /summary
@IvanNewsBot123: 🤖 Создаю ИИ-саммари...

📰 Саммари новостей за 15.01.2024

🏛️ ПОЛИТИКА (2 новости):
• Президент подписал новый закон о цифровизации
• Министр экономики выступил с заявлением о росте ВВП

💰 ЭКОНОМИКА (3 новости):
• Рубль укрепился на 2% к доллару
• Инфляция замедлилась до 4.1%
• ЦБ сохранил ключевую ставку на уровне 16%
```

### 2. **Подписка на каналы**

#### Через Telegram бота
```
Пользователь → Telegram бот → Команды → Управление каналами
     ↓              ↓           ↓            ↓
1. /start → 2. /add_channel → 3. Вводит @channel → 4. Бот подписывается
```

**Команды бота:**
- `/start` - начало работы
- `/add_channel @channel_name` - добавить канал
- `/remove_channel @channel_name` - удалить канал
- `/list_channels` - показать все каналы
- `/categories` - управление категориями
- `/news` - получить новости
- `/summary` - получить саммари

### 3. **Система категорий**

#### Создание категорий
```
Пользователь → Telegram бот → Команды → Создание категории → Настройка правил
     ↓              ↓           ↓            ↓                    ↓
1. /categories → 2. /create_category → 3. Вводит название → 4. Настраивает ключевые слова
```

**Возможности:**
- **Ручное создание:** Пользователь создает категории сам
- **Автоматическая категоризация:** ИИ определяет категорию по ключевым словам
- **Гибкие правила:** Настройка правил для автоматической категоризации
- **Цветовая кодировка:** Каждая категория имеет свой цвет

#### Примеры категорий:
- 🏛️ **Политика** - ключевые слова: "выборы", "президент", "правительство"
- 💰 **Экономика** - ключевые слова: "рубль", "инфляция", "ВВП"
- 🚀 **Технологии** - ключевые слова: "ИИ", "криптовалюта", "стартап"
- 🌍 **Мир** - ключевые слова: "война", "мир", "международные"

### 4. **Просмотр новостей**

#### Через Telegram бота
```
Пользователь → Telegram бот → Команды → Получение новостей
     ↓              ↓           ↓            ↓
1. /news → 2. Выбирает категорию → 3. Получает новости → 4. Читает
```

**Команды для просмотра:**
- `/news` - последние новости
- `/news politics` - новости по политике
- `/news tech` - новости по технологиям
- `/search "ключевые слова"` - поиск по тексту
- `/favorites` - избранные новости

**Функции:**
- **Фильтрация по категориям** - просмотр новостей определенной темы
- **Поиск** - поиск по тексту новостей
- **Сортировка** - по дате, релевантности, популярности
- **Избранное** - сохранение интересных новостей
- **Поделиться** - отправка новости в Telegram

### 5. **ИИ саммари**

#### Создание саммари
```
Пользователь → Запрос саммари → ИИ обработка → Получение результата
     ↓              ↓              ↓              ↓
1. Выбирает период → 2. Выбирает категории → 3. OpenAI API → 4. Получает саммари
```

**Типы саммари:**
- **По категории** - саммари новостей определенной темы
- **По времени** - саммари за день/неделю/месяц
- **По всем каналам** - общий обзор всех новостей
- **Персонализированное** - на основе интересов пользователя

#### Пример саммари:
```
📰 Саммари новостей за 15.01.2024

🏛️ ПОЛИТИКА (5 новостей):
• Президент подписал новый закон о цифровизации
• Министр экономики выступил с заявлением о росте ВВП
• Парламент одобрил изменения в налоговом кодексе

💰 ЭКОНОМИКА (3 новости):
• Рубль укрепился на 2% к доллару
• Инфляция замедлилась до 4.1%
• ЦБ сохранил ключевую ставку на уровне 16%

🚀 ТЕХНОЛОГИИ (4 новости):
• OpenAI представила новую модель GPT-5
• Tesla запустила производство в России
• Криптовалюты выросли на 15%
```

### 6. **Уведомления и расписание**

#### Настройка уведомлений
```
Пользователь → Настройки → Уведомления → Расписание
     ↓              ↓           ↓            ↓
1. Заходит в настройки → 2. Выбирает тип → 3. Настраивает время → 4. Сохраняет
```

**Типы уведомлений:**
- **Ежедневные дайджесты** - в определенное время
- **Срочные новости** - по важным темам
- **Еженедельные обзоры** - сводка за неделю
- **Персональные** - на основе интересов

### 7. **База данных (PostgreSQL)**

#### Основные таблицы:

```sql
-- Пользователи
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    bot_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Боты пользователей
CREATE TABLE user_bots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    bot_token VARCHAR(255) UNIQUE NOT NULL,
    bot_username VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Каналы
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subscribers_count INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Подписки пользователей на каналы
CREATE TABLE user_channel_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    channel_id INTEGER REFERENCES channels(id),
    bot_id INTEGER REFERENCES user_bots(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, channel_id)
);

-- Категории пользователей
CREATE TABLE user_categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7), -- HEX цвет
    keywords TEXT[], -- Массив ключевых слов
    is_auto BOOLEAN DEFAULT false, -- Автоматическая категоризация
    created_at TIMESTAMP DEFAULT NOW()
);

-- Новости
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id),
    telegram_message_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    media_urls TEXT[],
    published_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Категоризация новостей
CREATE TABLE news_categories (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES news(id),
    category_id INTEGER REFERENCES user_categories(id),
    confidence FLOAT, -- Уверенность ИИ в категоризации
    created_at TIMESTAMP DEFAULT NOW()
);

-- ИИ саммари
CREATE TABLE ai_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    categories TEXT[], -- Категории, по которым создано саммари
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 8. **API Endpoints (FastAPI)**

```python
# Аутентификация
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh

# Управление каналами
GET    /api/v1/channels/                    # Получить каналы пользователя
POST   /api/v1/channels/                    # Добавить канал
DELETE /api/v1/channels/{channel_id}        # Удалить канал

# Управление категориями
GET    /api/v1/categories/                  # Получить категории
POST   /api/v1/categories/                  # Создать категорию
PUT    /api/v1/categories/{category_id}     # Обновить категорию
DELETE /api/v1/categories/{category_id}     # Удалить категорию

# Новости
GET    /api/v1/news/                        # Получить новости
GET    /api/v1/news/category/{category_id}  # Новости по категории
GET    /api/v1/news/search                  # Поиск новостей

# ИИ функции
POST   /api/v1/ai/summary                   # Создать саммари
POST   /api/v1/ai/categorize                # Категоризировать новости
GET    /api/v1/ai/trends                    # Получить тренды

# Уведомления
GET    /api/v1/notifications/               # Получить уведомления
POST   /api/v1/notifications/settings       # Настроить уведомления
```

### 9. **Пользовательский интерфейс (Telegram + Web App)**

#### Inline Keyboard (Встроенная клавиатура)
```python
# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📰 Новости", callback_data="news")],
    [InlineKeyboardButton(text="📂 Каналы", callback_data="channels")],
    [InlineKeyboardButton(text="🏷️ Категории", callback_data="categories")],
    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="🌐 Web App", web_app=WebAppInfo(url="https://yourapp.com/webapp"))]
])

# Меню категорий
categories_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏛️ Политика", callback_data="category_politics")],
    [InlineKeyboardButton(text="💰 Экономика", callback_data="category_economics")],
    [InlineKeyboardButton(text="🚀 Технологии", callback_data="category_tech")],
    [InlineKeyboardButton(text="🌍 Мир", callback_data="category_world")],
    [InlineKeyboardButton(text="➕ Создать категорию", callback_data="create_category")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
])

# Меню управления каналами
channels_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Добавить канал", callback_data="add_channel")],
    [InlineKeyboardButton(text="📋 Список каналов", callback_data="list_channels")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
])
```

#### Web App (Встроенное веб-приложение)
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Aggregator</title>
    <link href="https://cdn.jsdelivr.net/npm/vuetify@3.4.0/dist/vuetify.min.css" rel="stylesheet">
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vuetify@3.4.0/dist/vuetify.min.js"></script>
</head>
<body>
    <div id="app">
        <v-app>
            <v-main>
                <v-container>
                    <!-- Дашборд -->
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-card>
                                <v-card-title>Всего каналов</v-card-title>
                                <v-card-text class="text-h4">{{ channelsCount }}</v-card-text>
                            </v-card>
                        </v-col>
                        
                        <v-col cols="12" md="9">
                            <v-card>
                                <v-card-title>Последние новости</v-card-title>
                                <v-card-text>
                                    <NewsCard 
                                        v-for="news in latestNews" 
                                        :key="news.id" 
                                        :news="news" 
                                    />
                                </v-card-text>
                            </v-card>
                        </v-col>
                    </v-row>
                    
                    <!-- Управление каналами -->
                    <v-card class="mt-4">
                        <v-card-title>
                            Управление каналами
                            <v-spacer></v-spacer>
                            <v-btn color="primary" @click="addChannelDialog = true">
                                Добавить канал
                            </v-btn>
                        </v-card-title>
                        
                        <v-card-text>
                            <v-data-table
                                :headers="headers"
                                :items="channels"
                                :loading="loading"
                            >
                                <template v-slot:item.actions="{ item }">
                                    <v-btn icon @click="removeChannel(item)">
                                        <v-icon>mdi-delete</v-icon>
                                    </v-btn>
                                </template>
                            </v-data-table>
                        </v-card-text>
                    </v-card>
                </v-container>
            </v-main>
        </v-app>
    </div>

    <script>
        const { createApp } = Vue;
        const { createVuetify } = Vuetify;

        const vuetify = createVuetify();

        createApp({
            data() {
                return {
                    channelsCount: 0,
                    latestNews: [],
                    channels: [],
                    loading: false,
                    addChannelDialog: false,
                    headers: [
                        { title: 'Название', key: 'title' },
                        { title: 'Подписчики', key: 'subscribers' },
                        { title: 'Действия', key: 'actions' }
                    ]
                }
            },
            methods: {
                async loadData() {
                    // Загрузка данных через Telegram Web App API
                    const data = await this.telegramApi.getUserData();
                    this.channelsCount = data.channelsCount;
                    this.latestNews = data.latestNews;
                    this.channels = data.channels;
                },
                async addChannel(channelName) {
                    // Добавление канала
                    await this.telegramApi.addChannel(channelName);
                    await this.loadData();
                },
                async removeChannel(channel) {
                    // Удаление канала
                    await this.telegramApi.removeChannel(channel.id);
                    await this.loadData();
                }
            },
            mounted() {
                this.loadData();
            }
        }).use(vuetify).mount('#app');
    </script>
</body>
</html>
```

#### Inline Query (Встроенный поиск)
```python
# Обработка inline запросов
@dp.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    query = inline_query.query.lower()
    
    # Поиск новостей по запросу
    news_results = await search_news(query, inline_query.from_user.id)
    
    # Формирование результатов
    results = []
    for news in news_results:
        results.append(InlineQueryResultArticle(
            id=str(news.id),
            title=news.title,
            description=news.preview,
            input_message_content=InputTextMessageContent(
                message_text=f"📰 {news.title}\n\n{news.content}\n\n🔗 {news.url}"
            ),
            thumb_url=news.image_url
        ))
    
    await inline_query.answer(results, cache_time=300)
```

### 10. **Процесс работы системы**

#### Реальное время (Webhook + Telethon):
1. **Мониторинг каналов** (мгновенно)
   - Telethon клиент подписан на обновления каналов
   - Новые сообщения обрабатываются мгновенно
   - Автоматическая категоризация через ИИ
   - Сохранение в базу данных

2. **Обработка новостей** (асинхронно)
   - Анализ тональности
   - Поиск дубликатов
   - Обновление статистики
   - Отправка уведомлений пользователям

3. **Уведомления** (по событиям)
   - Мгновенные уведомления о важных новостях
   - Ежедневные дайджесты по расписанию
   - Персональные рекомендации

#### Пользовательский сценарий:

**1. Регистрация через Telegram:**
```
Пользователь → @NewsAggregatorBot → /register → Ввод данных → Получение личного бота
     ↓              ↓                    ↓           ↓              ↓
1. Находит бота → 2. /start → 3. /register → 4. Email, имя → 5. @UserBot123
```

**2. Настройка через личного бота:**
```
Пользователь → @UserBot123 → Команды → Добавление каналов → Создание категорий
     ↓              ↓           ↓            ↓                ↓
1. /start → 2. /add_channel → 3. @channel → 4. /categories → 5. Настройка
```

**3. Просмотр новостей:**
```
Пользователь → @UserBot123 → /news → Выбор категории → Чтение новостей
     ↓              ↓           ↓            ↓              ↓
1. Открывает бота → 2. /news → 3. Выбирает тему → 4. Читает → 5. /summary
```

**4. Расширенное управление (Web App):**
```
Пользователь → @UserBot123 → /webapp → Встроенное приложение → Управление
     ↓              ↓           ↓            ↓                    ↓
1. Открывает бота → 2. Нажимает кнопку → 3. Web App → 4. Управляет каналами → 5. Аналитика
```

**5. Полный цикл работы:**
- **Регистрация** → Telegram-бот создает аккаунт и личного бота
- **Настройка** → Добавление каналов и категорий через бота
- **Просмотр** → Чтение новостей в Telegram (текст + Web App)
- **Анализ** → Получение ИИ-саммари по команде
- **Управление** → Настройка уведомлений и фильтров через Web App

## 🚀 Технологический стек

### 🐍 Python + aiogram + Web App

**Backend (Python):**
- **Bot Framework:** aiogram 3.x (асинхронный, современный)
- **Channel Monitor:** Telethon (реальное время мониторинг каналов)
- **Web Framework:** FastAPI (для Web App)
- **База данных:** PostgreSQL + SQLAlchemy 2.0
- **ИИ:** OpenAI API + transformers (локальные модели)
- **Планировщик:** APScheduler
- **Кэширование:** Redis
- **Валидация:** Pydantic v2

**Frontend (Web App):**
- **HTML5** - семантическая разметка
- **CSS3** - современные стили и анимации
- **JavaScript (ES6+)** - интерактивность
- **Vue.js 3** - реактивность (опционально)
- **Vuetify** - Material Design компоненты

**Структура проекта:**
```
project_owl/
├── backend/            # Python бэкенд
│   ├── main.py        # Главный файл
│   ├── bots/          # Боты
│   │   ├── main_bot.py    # Главный бот регистрации
│   │   └── user_bot.py    # Личные боты пользователей
│   ├── services/      # Сервисы
│   │   ├── telethon_monitor.py  # Мониторинг каналов
│   │   ├── news_processor.py    # Обработка новостей
│   │   └── ai_service.py        # ИИ сервисы
│   ├── models/        # Модели БД
│   ├── utils/         # Утилиты
│   └── config/        # Конфигурация
├── webapp/            # Web App
│   ├── index.html     # Главная страница
│   ├── css/           # Стили
│   ├── js/            # JavaScript
│   └── components/    # Vue компоненты
└── requirements.txt   # Зависимости Python
```

**Пример Telethon монитора:**
```python
# backend/services/telethon_monitor.py
from telethon import TelegramClient, events
from telethon.tl.types import Channel
import asyncio
import logging

class ChannelMonitor:
    def __init__(self, api_id: int, api_hash: str, session_name: str):
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.monitored_channels = set()
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Запуск мониторинга каналов"""
        await self.client.start()
        self.logger.info("Telethon monitor started")
    
    async def add_channel(self, channel_username: str, user_id: int):
        """Добавление канала для мониторинга"""
        try:
            channel = await self.client.get_entity(channel_username)
            if isinstance(channel, Channel):
                self.monitored_channels.add((channel.id, user_id))
                
                # Регистрируем обработчик для этого канала
                @self.client.on(events.NewMessage(chats=channel))
                async def handler(event):
                    await self.process_new_message(event, user_id)
                
                self.logger.info(f"Added channel {channel_username} for user {user_id}")
        except Exception as e:
            self.logger.error(f"Error adding channel {channel_username}: {e}")
    
    async def process_new_message(self, event, user_id: int):
        """Обработка нового сообщения из канала"""
        message = event.message
        
        # Сохраняем новость в базу данных
        news_data = {
            'channel_id': event.chat_id,
            'message_id': message.id,
            'content': message.text or '',
            'media_urls': self.extract_media_urls(message),
            'published_at': message.date,
            'user_id': user_id
        }
        
        # Отправляем на обработку
        await self.send_to_processor(news_data)
        
        self.logger.info(f"Processed new message from channel {event.chat_id}")
    
    def extract_media_urls(self, message):
        """Извлечение URL медиафайлов из сообщения"""
        urls = []
        if message.photo:
            urls.append(f"photo_{message.photo.id}")
        if message.video:
            urls.append(f"video_{message.video.id}")
        if message.document:
            urls.append(f"document_{message.document.id}")
        return urls
    
    async def send_to_processor(self, news_data: dict):
        """Отправка данных на обработку"""
        # Здесь можно отправить в очередь или напрямую в процессор
        pass

# Использование
async def main():
    monitor = ChannelMonitor(
        api_id=YOUR_API_ID,
        api_hash=YOUR_API_HASH,
        session_name='news_monitor'
    )
    
    await monitor.start()
    
    # Добавляем каналы для мониторинга
    await monitor.add_channel('@meduzaproject', user_id=123)
    await monitor.add_channel('@tass_agency', user_id=123)
    
    # Запускаем мониторинг
    await monitor.client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
```

**Преимущества:**
- ⚡ Высокая производительность
- 🤖 Отличная поддержка ИИ-библиотек
- 🔧 Простота разработки и тестирования
- 📱 Полная интеграция с Telegram
- 🎨 Встроенные интерфейсы Telegram
- 🚀 Быстрая разработка MVP

## 🎨 Интерфейсы системы

### Telegram интерфейсы:
1. **Inline Keyboard (Кнопки)**
   - Главное меню навигации
   - Выбор категорий новостей
   - Управление каналами
   - Настройки уведомлений

2. **Web App (Встроенное приложение)**
   - Дашборд с статистикой
   - Управление каналами
   - Настройка категорий
   - Аналитика и графики

3. **Inline Query (Поиск)**
   - Быстрый поиск новостей
   - Автодополнение
   - Превью новостей

4. **Команды бота**
   - `/news` - просмотр новостей
   - `/channels` - управление каналами
   - `/categories` - настройка категорий
   - `/summary` - ИИ-саммари

### Компоненты Web App:
- **NewsCard** - карточка новости с превью
- **ChannelCard** - карточка канала с статистикой
- **CategoryChip** - чип категории
- **SearchBar** - поиск с автодополнением
- **FilterPanel** - панель фильтров
- **AISummary** - ИИ-саммари новостей

## 🔧 Технические детали

### API Endpoints (пример для Python + FastAPI):
```
GET  /api/v1/news/              # Получить новости
POST /api/v1/news/              # Создать новость
GET  /api/v1/channels/          # Получить каналы
POST /api/v1/channels/          # Добавить канал
GET  /api/v1/categories/        # Получить категории
POST /api/v1/categories/        # Создать категорию
GET  /api/v1/ai/summary/        # Получить саммари
POST /api/v1/ai/analyze/        # Анализ новости
```

### База данных (PostgreSQL):
```sql
-- Таблица каналов
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subscribers_count INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица новостей
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id),
    telegram_message_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    media_urls TEXT[],
    published_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Таблица категорий
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7), -- HEX цвет
    keywords TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 План разработки

### Этап 1: MVP (2-3 недели)
- [ ] Настройка проекта (Python + aiogram + Telethon + FastAPI)
- [ ] Главный бот для регистрации
- [ ] **Система пула предварительно созданных ботов** (100-500 ботов)
- [ ] Базовая структура базы данных
- [ ] **Telethon монитор с rate limiting** для каналов
- [ ] Подписка на каналы через бота
- [ ] **Оптимизированный сбор новостей** через Telethon с очередями

### Этап 2: Telegram интерфейсы (2-3 недели)
- [ ] **Inline Keyboard меню с соблюдением лимитов** (макс 100 кнопок)
- [ ] **Команды бота с rate limiting** (30 сообщений/сек)
- [ ] **Web App (базовая версия)** с оптимизацией
- [ ] **Inline Query поиск с кэшированием**
- [ ] **Callback Query обработка с очередями**

### Этап 3: Категоризация (2-3 недели)
- [ ] Система категорий
- [ ] Автоматическая категоризация
- [ ] Управление категориями через бота
- [ ] Фильтрация новостей по категориям

### Этап 4: ИИ интеграция (2-3 недели)
- [ ] **OpenAI API интеграция с rate limiting**
- [ ] **Создание саммари с очередями**
- [ ] **Анализ тональности с батчевой обработкой**
- [ ] **Умная категоризация с кэшированием**
- [ ] **Персонализация рекомендаций с оптимизацией**

### Этап 5: Продвинутые функции (2-3 недели)
- [ ] Расширенный Web App с Vuetify
- [ ] Уведомления и расписание
- [ ] Аналитика и статистика
- [ ] Экспорт данных
- [ ] Оптимизация производительности

## 💡 Дополнительные возможности

### ИИ функции:
- **Автоматическое саммари** - краткое изложение новостей
- **Категоризация** - автоматическое определение темы
- **Анализ тональности** - позитивные/негативные новости
- **Дубликаты** - поиск похожих новостей
- **Персонализация** - рекомендации на основе интересов

### Интеграции:
- **Telegram Bot API** - основной источник данных
- **OpenAI API** - ИИ-анализ
- **News APIs** - дополнительные источники
- **Social Media** - интеграция с Twitter, VK
- **RSS** - поддержка RSS-лент

## 🎯 Рекомендация

**Для вашего проекта рекомендую: Python + aiogram + Web App**

**Почему именно этот стек:**
1. **Быстрая разработка** - можно быстро создать MVP
2. **Простота** - все в Telegram, не нужен отдельный сайт
3. **Красивый интерфейс** - Web App с Vuetify компонентами
4. **Отличная производительность** - aiogram + FastAPI очень быстрые
5. **ИИ интеграция** - Python лучший для машинного обучения
6. **Масштабируемость** - легко добавлять новые функции
7. **Сообщество** - большое количество примеров и решений
8. **Мобильность** - работает на всех устройствах через Telegram

Этот стек позволит создать современное, функциональное приложение с минимальными затратами времени на разработку и поддержку.
