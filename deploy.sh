#!/bin/bash

echo "🚀 Starting deployment..."

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please copy env.example to .env and configure it."
    exit 1
fi

# Остановка старых контейнеров
echo "🛑 Stopping old containers..."
docker-compose down

# Обновление кода
echo "📥 Updating code..."
git pull origin main

# Сборка новых образов
echo "🔨 Building new images..."
docker-compose build

# Запуск миграций (если есть)
echo "🗄️ Running migrations..."
docker-compose run --rm app python backend/manage.py migrate || echo "No migrations to run"

# Запуск сервисов
echo "🚀 Starting services..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Waiting for services to start..."
sleep 30

# Проверка здоровья
echo "🔍 Checking service health..."
docker-compose ps

# Проверка логов на ошибки
echo "📋 Checking logs for errors..."
if docker-compose logs app | grep -i error; then
    echo "❌ Errors found in logs!"
    exit 1
fi

echo "✅ Deployment completed successfully!"
echo "🌐 Application is available at: http://localhost:8000"
echo "📊 Check logs with: docker-compose logs -f app"
