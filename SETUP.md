# 🛠️ Руководство по настройке проекта

## 📋 Что нужно для тестирования базовой структуры

### **1. 🖥️ Сервер (VPS/Облако)**
**Обязательно нужен, потому что:**
- Telethon требует постоянного подключения
- Боты должны работать 24/7
- Нужен публичный IP для webhook'ов

**Варианты:**
- **VPS** (DigitalOcean, Vultr, Timeweb) - ~$5-10/месяц
- **Облако** (AWS, Google Cloud, Yandex Cloud) - ~$5-15/месяц
- **VDS** (Beget, REG.RU) - ~$3-8/месяц

**Минимальные требования:**
- 1 CPU, 1GB RAM, 20GB SSD
- Ubuntu 20.04+ или CentOS 8+
- Python 3.9+

### **2. 🤖 Telegram боты**

#### **A. Главный бот (для регистрации):**
1. Идем к [@BotFather](https://t.me/BotFather)
2. `/newbot` → создаем бота
3. Получаем токен: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
4. Настраиваем команды: `/setcommands`

#### **B. Тестовые личные боты:**
- Создаем 2-3 тестовых бота через BotFather
- Каждый для тестирования разных пользователей

### **3. 🔑 Telegram API ключи (для Telethon)**

#### **Получение api_id и api_hash:**
1. Идем на [my.telegram.org](https://my.telegram.org)
2. Входим в свой аккаунт
3. "API development tools"
4. Создаем приложение:
   - App title: "News Aggregator"
   - Short name: "news_agg"
   - Platform: "Desktop"
5. Получаем:
   - `api_id`: 12345678
   - `api_hash`: "abcdef1234567890abcdef1234567890"

### **4. 🗄️ База данных**

#### **Варианты:**
- **PostgreSQL** (рекомендуется) - на том же VPS
- **SQLite** (для тестирования) - локально
- **Облачная БД** (AWS RDS, Yandex Managed PostgreSQL)

### **5. 🔧 Переменные окружения**

Создаем файл `.env`:
```env
# Telegram Bot Tokens
MAIN_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TEST_USER_BOT_1=987654321:XYZabcDEFghiJKLmnoPQRstuvwxyz
TEST_USER_BOT_2=456789123:QWErtYUIopASDfghJKLzxcVBNm

# Telegram API (для Telethon)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/news_aggregator
# или для SQLite: sqlite:///./news_aggregator.db

# Redis (для кэширования)
REDIS_URL=redis://localhost:6379/0

# OpenAI API (для ИИ)
OPENAI_API_KEY=sk-abcdef1234567890abcdef1234567890

# Web App URL
WEBAPP_URL=https://yourdomain.com/webapp

# Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### **6. 📁 Структура проекта**

```
project_owl/
├── .env                    # Переменные окружения
├── .gitignore             # Игнорируемые файлы
├── requirements.txt       # Python зависимости
├── docker-compose.yml     # Docker контейнеры
├── Dockerfile            # Docker образ
├── README.md             # Документация
├── SETUP.md              # Это руководство
├── backend/              # Python бэкенд
│   ├── main.py          # Главный файл
│   ├── config/          # Конфигурация
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── bots/            # Боты
│   │   ├── __init__.py
│   │   ├── main_bot.py  # Главный бот
│   │   └── user_bot.py  # Личные боты
│   ├── services/        # Сервисы
│   │   ├── __init__.py
│   │   ├── telethon_monitor.py
│   │   ├── news_processor.py
│   │   └── ai_service.py
│   ├── models/          # Модели БД
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   └── utils/           # Утилиты
│       ├── __init__.py
│       └── helpers.py
└── webapp/              # Web App
    ├── index.html
    ├── css/
    ├── js/
    └── components/
```

### **7. 🐍 Python зависимости**

Файл `requirements.txt`:
```
# Bot frameworks
aiogram==3.4.1
telethon==1.34.0

# Web framework
fastapi==0.104.1
uvicorn==0.24.0

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0  # PostgreSQL driver
alembic==1.12.1  # Миграции БД

# Redis
redis==5.0.1
aioredis==2.0.1

# AI
openai==1.3.7
transformers==4.35.2

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
apscheduler==3.10.4
```

---

## 🐳 Вариант с Docker + GitHub Actions

### **Преимущества Docker подхода:**
- ✅ **Изоляция** - все зависимости в контейнерах
- ✅ **Портабельность** - работает одинаково везде
- ✅ **Простота развертывания** - одна команда запуска
- ✅ **CI/CD** - автоматическое тестирование через GitHub Actions
- ✅ **Масштабируемость** - легко добавлять сервисы

### **1. 🐳 Docker конфигурация**

#### **Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY backend/ ./backend/
COPY webapp/ ./webapp/

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["python", "backend/main.py"]
```

#### **docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/news_aggregator
      - REDIS_URL=redis://redis:6379/0
      - MAIN_BOT_TOKEN=${MAIN_BOT_TOKEN}
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app/backend
      - ./webapp:/app/webapp
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=news_aggregator
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./webapp:/usr/share/nginx/html
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### **2. 🚀 GitHub Actions для автоматического тестирования**

#### **.github/workflows/test.yml:**
```yaml
name: Test and Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: news_aggregator_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:password@localhost:5432/news_aggregator_test
        REDIS_URL: redis://localhost:6379/0
        MAIN_BOT_TOKEN: ${{ secrets.TEST_BOT_TOKEN }}
        TELEGRAM_API_ID: ${{ secrets.TELEGRAM_API_ID }}
        TELEGRAM_API_HASH: ${{ secrets.TELEGRAM_API_HASH }}
      run: |
        pytest backend/tests/ -v

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: |
        docker build -t news-aggregator:latest .
    
    - name: Test Docker container
      run: |
        docker-compose -f docker-compose.test.yml up -d
        sleep 30
        docker-compose -f docker-compose.test.yml down

  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to VPS
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USERNAME }}
        key: ${{ secrets.VPS_SSH_KEY }}
        script: |
          cd /home/newsbot/project_owl
          git pull origin main
          docker-compose down
          docker-compose up -d --build
```

### **3. 🔧 Настройка GitHub Secrets**

В настройках репозитория GitHub добавляем:
- `TEST_BOT_TOKEN` - токен тестового бота
- `TELEGRAM_API_ID` - API ID для Telethon
- `TELEGRAM_API_HASH` - API Hash для Telethon
- `VPS_HOST` - IP адрес VPS
- `VPS_USERNAME` - пользователь VPS
- `VPS_SSH_KEY` - SSH ключ для доступа к VPS

### **4. 🚀 Локальная разработка с Docker**

#### **Запуск для разработки:**
```bash
# Клонирование репозитория
git clone https://github.com/yourusername/project_owl.git
cd project_owl

# Создание .env файла
cp .env.example .env
# Редактируем .env с реальными значениями

# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f app

# Остановка
docker-compose down
```

#### **Команды для разработки:**
```bash
# Пересборка после изменений
docker-compose up -d --build

# Выполнение команд в контейнере
docker-compose exec app python backend/manage.py migrate
docker-compose exec app python backend/manage.py createsuperuser

# Просмотр базы данных
docker-compose exec db psql -U postgres -d news_aggregator

# Очистка всех данных
docker-compose down -v
```

### **5. 📊 Мониторинг и логи**

#### **docker-compose.monitoring.yml:**
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml

volumes:
  grafana_data:
```

### **6. 🔄 Автоматическое развертывание**

#### **Скрипт развертывания (deploy.sh):**
```bash
#!/bin/bash

echo "🚀 Starting deployment..."

# Остановка старых контейнеров
docker-compose down

# Обновление кода
git pull origin main

# Сборка новых образов
docker-compose build

# Запуск миграций
docker-compose run --rm app python backend/manage.py migrate

# Запуск сервисов
docker-compose up -d

# Проверка здоровья
sleep 30
docker-compose ps

echo "✅ Deployment completed!"
```

### **7. 💰 Стоимость с Docker**

- **VPS:** $5-10/месяц
- **GitHub Actions:** Бесплатно (2000 минут/месяц)
- **Docker Hub:** Бесплатно (публичные репозитории)
- **Мониторинг:** Бесплатно (Prometheus + Grafana)
- **Итого:** $5-10/месяц

### **8. 🎯 Преимущества Docker подхода**

1. **Быстрый старт** - `docker-compose up` и все работает
2. **Изоляция** - каждый сервис в своем контейнере
3. **Масштабируемость** - легко добавлять новые сервисы
4. **CI/CD** - автоматическое тестирование и деплой
5. **Портабельность** - работает одинаково везде
6. **Откат** - легко вернуться к предыдущей версии
7. **Мониторинг** - встроенные инструменты

### **9. 🚀 Быстрый старт**

```bash
# 1. Клонируем репозиторий
git clone https://github.com/yourusername/project_owl.git
cd project_owl

# 2. Настраиваем переменные
cp .env.example .env
# Редактируем .env

# 3. Запускаем все сервисы
docker-compose up -d

# 4. Проверяем статус
docker-compose ps

# 5. Смотрим логи
docker-compose logs -f app
```

**Готово!** 🎉 Все сервисы запущены и готовы к работе.
