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

echo -e "${BLUE}⚡ Быстрое развертывание для тестирования...${NC}"

cd "$PROJECT_DIR"

# Остановка контейнеров
echo -e "${YELLOW}Остановка контейнеров...${NC}"
docker-compose down || true

# Обновление кода
echo -e "${YELLOW}Обновление кода...${NC}"
git pull origin main

# Перезапуск
echo -e "${YELLOW}Перезапуск сервисов...${NC}"
docker-compose up -d --build

# Проверка
echo -e "${YELLOW}Проверка статуса...${NC}"
sleep 10
docker-compose ps

echo -e "${GREEN}✅ Быстрое развертывание завершено!${NC}"
echo -e "${BLUE}📝 Логи: docker-compose logs -f app${NC}"
