#!/bin/bash

# 🚀 Скрипт автоматического развертывания на VPS
# Использование: ./deploy.sh [branch] [environment]

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Параметры
BRANCH=${1:-main}
ENVIRONMENT=${2:-production}
PROJECT_DIR="/home/newsbot/project_owl"

# Настройка репозитория (замените на ваш)
GITHUB_USERNAME="YOUR_USERNAME"
GITHUB_REPO="project_owl"

# Автоматическое определение URL репозитория
if [ -n "$GITHUB_TOKEN" ]; then
    REPO_URL="https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$GITHUB_REPO.git"
elif [ -f ~/.ssh/id_ed25519 ] || [ -f ~/.ssh/id_rsa ]; then
    REPO_URL="git@github.com:$GITHUB_USERNAME/$GITHUB_REPO.git"
else
    REPO_URL="https://github.com/$GITHUB_USERNAME/$GITHUB_REPO.git"
fi

echo -e "${BLUE}🚀 Начинаем развертывание проекта...${NC}"
echo -e "${YELLOW}Ветка: ${BRANCH}${NC}"
echo -e "${YELLOW}Окружение: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Репозиторий: ${REPO_URL}${NC}"

# Проверка настройки репозитория
if [ "$GITHUB_USERNAME" = "YOUR_USERNAME" ]; then
    echo -e "${RED}⚠️  ВНИМАНИЕ: Необходимо настроить GITHUB_USERNAME в скрипте!${NC}"
    echo -e "${YELLOW}Отредактируйте файл deploy.sh и замените YOUR_USERNAME на ваш GitHub username${NC}"
    exit 1
fi

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    error "Docker не установлен! Установите Docker сначала."
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose не установлен! Установите Docker Compose сначала."
fi

log "Проверка Docker... ✅"

# Создание директории проекта если не существует
if [ ! -d "$PROJECT_DIR" ]; then
    log "Создание директории проекта..."
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Остановка старых контейнеров
log "Остановка старых контейнеров..."
docker-compose down --remove-orphans || true

# Создание резервной копии .env если существует
if [ -f ".env" ]; then
    log "Создание резервной копии .env..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# Клонирование или обновление репозитория
if [ -d ".git" ]; then
    log "Обновление кода из GitHub..."
    git fetch origin
    git reset --hard origin/$BRANCH
    git clean -fd
else
    log "Клонирование репозитория..."
    git clone $REPO_URL .
    git checkout $BRANCH
fi

log "Код обновлен из GitHub ✅"

# Создание .env файла если не существует
if [ ! -f ".env" ]; then
    log "Создание .env файла из примера..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Необходимо настроить .env файл!${NC}"
    echo -e "${YELLOW}Отредактируйте .env файл и запустите скрипт снова.${NC}"
    exit 1
fi

# Проверка наличия необходимых переменных
log "Проверка конфигурации..."
if ! grep -q "MAIN_BOT_TOKEN=" .env; then
    error "MAIN_BOT_TOKEN не найден в .env файле!"
fi

if ! grep -q "TELEGRAM_API_ID=" .env; then
    error "TELEGRAM_API_ID не найден в .env файле!"
fi

if ! grep -q "TELEGRAM_API_HASH=" .env; then
    error "TELEGRAM_API_HASH не найден в .env файле!"
fi

log "Конфигурация проверена ✅"

# Сборка и запуск контейнеров
log "Сборка Docker образов..."
docker-compose build --no-cache

log "Запуск сервисов..."
docker-compose up -d

# Ожидание запуска сервисов
log "Ожидание запуска сервисов..."
sleep 30

# Проверка статуса контейнеров
log "Проверка статуса контейнеров..."
docker-compose ps

# Проверка логов на ошибки
log "Проверка логов приложения..."
if docker-compose logs app | grep -i error; then
    echo -e "${YELLOW}⚠️  Найдены ошибки в логах приложения${NC}"
fi

# Проверка доступности приложения
log "Проверка доступности приложения..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "Приложение доступно ✅"
else
    echo -e "${YELLOW}⚠️  Приложение может быть недоступно${NC}"
fi

# Очистка старых образов
log "Очистка неиспользуемых Docker образов..."
docker image prune -f

log "🎉 Развертывание завершено!"
echo -e "${GREEN}✅ Проект успешно развернут на VPS${NC}"
echo -e "${BLUE}📊 Статус сервисов:${NC}"
docker-compose ps

echo -e "${BLUE}📝 Полезные команды:${NC}"
echo -e "${YELLOW}  Просмотр логов: docker-compose logs -f app${NC}"
echo -e "${YELLOW}  Остановка: docker-compose down${NC}"
echo -e "${YELLOW}  Перезапуск: docker-compose restart${NC}"
echo -e "${YELLOW}  Обновление: ./deploy.sh${NC}"