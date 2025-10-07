#!/bin/bash

# 🛠️ Настройка VPS для проекта
# Использование: ./setup-vps.sh

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛠️ Настройка VPS для проекта...${NC}"

# Обновление системы
echo -e "${YELLOW}Обновление системы...${NC}"
sudo apt update && sudo apt upgrade -y

# Установка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Установка Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Установка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Установка Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Установка Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Установка Git...${NC}"
    sudo apt install git -y
fi

# Создание пользователя newsbot
if ! id "newsbot" &>/dev/null; then
    echo -e "${YELLOW}Создание пользователя newsbot...${NC}"
    sudo useradd -m -s /bin/bash newsbot
    sudo usermod -aG docker newsbot
fi

# Создание директории проекта
echo -e "${YELLOW}Создание директории проекта...${NC}"
sudo mkdir -p /home/newsbot/project_owl
sudo chown newsbot:newsbot /home/newsbot/project_owl

# Установка прав на скрипты
echo -e "${YELLOW}Настройка прав доступа...${NC}"
chmod +x /home/newsbot/project_owl/deploy.sh
chmod +x /home/newsbot/project_owl/quick-deploy.sh

# Создание systemd сервиса для автозапуска
echo -e "${YELLOW}Создание systemd сервиса...${NC}"
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

echo -e "${GREEN}✅ VPS настроен!${NC}"
echo -e "${BLUE}📝 Следующие шаги:${NC}"
echo -e "${YELLOW}1. Переключитесь на пользователя newsbot: su - newsbot${NC}"
echo -e "${YELLOW}2. Перейдите в директорию: cd /home/newsbot/project_owl${NC}"
echo -e "${YELLOW}3. Запустите развертывание: ./deploy.sh${NC}"
echo -e "${YELLOW}4. Настройте .env файл с вашими токенами${NC}"

