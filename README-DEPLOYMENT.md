# 🚀 Руководство по развертыванию на VPS

## 📋 Быстрый старт

### **1. Подготовка VPS**

#### **Автоматическая настройка:**
```bash
# Скачиваем и запускаем скрипт настройки
curl -fsSL https://raw.githubusercontent.com/rdeword/project_owl/main/setup-vps.sh | bash
```

#### **Ручная настройка:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка Git
sudo apt install git -y
```

### **2. Развертывание проекта**

#### **Полное развертывание:**
```bash
# Клонирование репозитория
git clone https://github.com/rdeword/project_owl.git
cd project_owl

# Настройка прав
chmod +x deploy.sh quick-deploy.sh setup-vps.sh

# Запуск развертывания
./deploy.sh
```

#### **Быстрое обновление:**
```bash
# Для обновления кода без полной пересборки
./quick-deploy.sh
```

## 🔧 Настройка конфигурации

### **1. Создание .env файла**

```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем конфигурацию
nano .env
```

### **2. Настройка переменных окружения**

```env
# Telegram Bot Tokens
MAIN_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Пул предварительно созданных ботов (100-500 ботов)
BOT_POOL_TOKEN_1=987654321:XYZabcDEFghiJKLmnoPQRstuvwxyz
BOT_POOL_TOKEN_2=456789123:QWErtYUIopASDfghJKLzxcVBNm
BOT_POOL_TOKEN_3=789123456:ASDFghjklZXCVbnmQWErtYUIop
# ... и так далее для всех ботов в пуле

# Telegram API (для Telethon)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/news_aggregator

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

# Rate Limiting (соблюдение ограничений Telegram API)
TELEGRAM_RATE_LIMIT=30  # сообщений в секунду
API_RATE_LIMIT=20       # запросов в секунду
MAX_BUTTONS_PER_MESSAGE=100  # кнопок в сообщении
MAX_COMMAND_LENGTH=256  # символов в команде
```

## 🚀 Команды развертывания

### **Основные команды:**

```bash
# Полное развертывание
./deploy.sh

# Развертывание конкретной ветки
./deploy.sh develop

# Быстрое обновление
./quick-deploy.sh

# Остановка сервисов
docker-compose down

# Просмотр логов
docker-compose logs -f app

# Перезапуск сервисов
docker-compose restart

# Обновление кода
git pull origin main && ./quick-deploy.sh
```

### **Полезные команды Docker:**

```bash
# Просмотр статуса контейнеров
docker-compose ps

# Просмотр логов конкретного сервиса
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f redis

# Подключение к контейнеру
docker-compose exec app bash

# Выполнение команд в контейнере
docker-compose exec app python backend/manage.py migrate
docker-compose exec app python backend/manage.py createsuperuser

# Очистка неиспользуемых образов
docker image prune -f

# Полная очистка
docker-compose down -v
docker system prune -a
```

## 📊 Мониторинг и логи

### **Просмотр логов:**

```bash
# Все сервисы
docker-compose logs -f

# Только приложение
docker-compose logs -f app

# Только база данных
docker-compose logs -f db

# Только Redis
docker-compose logs -f redis

# Последние 100 строк
docker-compose logs --tail=100 app
```

### **Мониторинг ресурсов:**

```bash
# Использование ресурсов
docker stats

# Дисковое пространство
df -h

# Память
free -h

# CPU
top
```

## 🔧 Настройка автозапуска

### **Systemd сервис:**

```bash
# Создание сервиса
sudo tee /etc/systemd/system/newsbot.service > /dev/null <<EOF
[Unit]
Description=News Bot Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/newsbot/project_owl
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=newsbot
Group=newsbot

[Install]
WantedBy=multi-user.target
EOF

# Включение автозапуска
sudo systemctl daemon-reload
sudo systemctl enable newsbot.service

# Управление сервисом
sudo systemctl start newsbot
sudo systemctl stop newsbot
sudo systemctl restart newsbot
sudo systemctl status newsbot
```

## 🚨 Устранение неполадок

### **Частые проблемы:**

#### **1. Контейнеры не запускаются:**
```bash
# Проверка логов
docker-compose logs app

# Проверка конфигурации
docker-compose config

# Пересборка образов
docker-compose build --no-cache
```

#### **2. Ошибки базы данных:**
```bash
# Проверка подключения к БД
docker-compose exec db psql -U postgres -d news_aggregator

# Выполнение миграций
docker-compose exec app python backend/manage.py migrate
```

#### **3. Проблемы с Redis:**
```bash
# Проверка Redis
docker-compose exec redis redis-cli ping

# Очистка кэша
docker-compose exec redis redis-cli flushall
```

#### **4. Ошибки Telegram API:**
```bash
# Проверка токенов в .env
grep -E "BOT_TOKEN|API_ID|API_HASH" .env

# Проверка логов бота
docker-compose logs app | grep -i telegram
```

### **Полная переустановка:**

```bash
# Остановка и удаление всех контейнеров
docker-compose down -v

# Удаление всех образов
docker system prune -a

# Очистка директории проекта
rm -rf /home/newsbot/project_owl

# Повторное развертывание
git clone https://github.com/rdeword/project_owl.git
cd project_owl
./deploy.sh
```

## 📈 Масштабирование

### **Увеличение ресурсов:**

```bash
# Редактирование docker-compose.yml
nano docker-compose.yml

# Добавление ограничений ресурсов
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### **Горизонтальное масштабирование:**

```bash
# Запуск нескольких экземпляров
docker-compose up -d --scale app=3

# Балансировка нагрузки через nginx
# (требует дополнительной настройки)
```

## 🔐 Безопасность

### **Настройка файрвола:**

```bash
# Установка UFW
sudo apt install ufw -y

# Настройка правил
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### **SSL сертификаты:**

```bash
# Установка Certbot
sudo apt install certbot -y

# Получение сертификата
sudo certbot certonly --standalone -d yourdomain.com
```

## 📞 Поддержка

### **Полезные ссылки:**
- 📚 [Документация Docker](https://docs.docker.com/)
- 📚 [Документация Docker Compose](https://docs.docker.com/compose/)
- 📚 [Telegram Bot API](https://core.telegram.org/bots/api)
- 📚 [Telethon документация](https://docs.telethon.dev/)

### **Логи для отладки:**
```bash
# Сбор всех логов
docker-compose logs > logs.txt 2>&1

# Отправка логов в поддержку
# (прикрепите файл logs.txt)
```

**Готово! Ваш проект развернут и готов к работе!** 🎉
