#!/bin/bash

# ⚡ Быстрое развертывание для тестирования
# Использование: ./quick-deploy.sh

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/newsbot/project_owl"

# Настройка репозитория (замените на ваш)
GITHUB_USERNAME="YOUR_USERNAME"
GITHUB_REPO="project_owl"

echo -e "${BLUE}⚡ Быстрое развертывание для тестирования...${NC}"

cd "$PROJECT_DIR"

# Остановка контейнеров
echo -e "${YELLOW}Остановка контейнеров...${NC}"
docker-compose down || true

# Обновление кода
echo -e "${YELLOW}Обновление кода...${NC}"

# Автоматическое определение способа обновления
if [ -n "$GITHUB_TOKEN" ]; then
    git pull https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$GITHUB_REPO.git main
elif [ -f ~/.ssh/id_ed25519 ] || [ -f ~/.ssh/id_rsa ]; then
    git pull origin main
else
    echo -e "${YELLOW}⚠️  Используется публичный репозиторий или настройте SSH/токен${NC}"
    git pull origin main
fi

# Перезапуск
echo -e "${YELLOW}Перезапуск сервисов...${NC}"
docker-compose up -d --build

# Проверка
echo -e "${YELLOW}Проверка статуса...${NC}"
sleep 10
docker-compose ps

echo -e "${GREEN}✅ Быстрое развертывание завершено!${NC}"
echo -e "${BLUE}📝 Логи: docker-compose logs -f app${NC}"

