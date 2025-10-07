#!/bin/bash

# 🔐 Скрипт настройки приватного GitHub репозитория
# Использование: ./setup-private-repo.sh

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔐 Настройка приватного GitHub репозитория${NC}"

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Запрос информации о репозитории
echo -e "${YELLOW}Введите данные вашего GitHub репозитория:${NC}"
read -p "GitHub username: " GITHUB_USERNAME
read -p "Repository name (default: project_owl): " GITHUB_REPO
GITHUB_REPO=${GITHUB_REPO:-project_owl}

echo -e "${YELLOW}Выберите способ аутентификации:${NC}"
echo "1) SSH ключи (рекомендуется)"
echo "2) Personal Access Token"
read -p "Ваш выбор (1-2): " AUTH_CHOICE

case $AUTH_CHOICE in
    1)
        log "Настройка SSH аутентификации..."
        
        # Проверка существования SSH ключа
        if [ ! -f ~/.ssh/id_ed25519 ] && [ ! -f ~/.ssh/id_rsa ]; then
            log "Генерация нового SSH ключа..."
            read -p "Введите ваш email для SSH ключа: " SSH_EMAIL
            ssh-keygen -t ed25519 -C "$SSH_EMAIL"
        fi
        
        # Запуск SSH агента
        eval "$(ssh-agent -s)"
        
        # Добавление ключа
        if [ -f ~/.ssh/id_ed25519 ]; then
            ssh-add ~/.ssh/id_ed25519
            SSH_KEY=$(cat ~/.ssh/id_ed25519.pub)
        else
            ssh-add ~/.ssh/id_rsa
            SSH_KEY=$(cat ~/.ssh/id_rsa.pub)
        fi
        
        echo -e "${YELLOW}📋 Скопируйте этот SSH ключ и добавьте в GitHub:${NC}"
        echo -e "${BLUE}$SSH_KEY${NC}"
        echo ""
        echo -e "${YELLOW}Инструкции:${NC}"
        echo "1. Перейдите в GitHub → Settings → SSH and GPG keys"
        echo "2. Нажмите 'New SSH key'"
        echo "3. Вставьте ключ выше"
        echo "4. Сохраните"
        echo ""
        read -p "Нажмите Enter после добавления ключа в GitHub..."
        
        # Тестирование SSH соединения
        log "Тестирование SSH соединения..."
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            log "SSH аутентификация успешна ✅"
        else
            error "SSH аутентификация не удалась. Проверьте настройки."
        fi
        
        # Обновление скриптов
        log "Обновление скриптов развертывания..."
        sed -i "s/YOUR_USERNAME/$GITHUB_USERNAME/g" deploy.sh
        sed -i "s/YOUR_USERNAME/$GITHUB_USERNAME/g" quick-deploy.sh
        
        ;;
        
    2)
        log "Настройка токен аутентификации..."
        
        echo -e "${YELLOW}Создайте Personal Access Token в GitHub:${NC}"
        echo "1. Перейдите в Settings → Developer settings → Personal access tokens"
        echo "2. Нажмите 'Generate new token (classic)'"
        echo "3. Выберите scope: 'repo' (Full control of private repositories)"
        echo "4. Скопируйте токен"
        echo ""
        read -p "Введите ваш Personal Access Token: " GITHUB_TOKEN
        
        # Сохранение токена в переменной окружения
        echo "export GITHUB_TOKEN=\"$GITHUB_TOKEN\"" >> ~/.bashrc
        export GITHUB_TOKEN="$GITHUB_TOKEN"
        
        # Обновление скриптов
        log "Обновление скриптов развертывания..."
        sed -i "s/YOUR_USERNAME/$GITHUB_USERNAME/g" deploy.sh
        sed -i "s/YOUR_USERNAME/$GITHUB_USERNAME/g" quick-deploy.sh
        
        ;;
        
    *)
        error "Неверный выбор. Запустите скрипт снова."
        ;;
esac

# Настройка Git
log "Настройка Git..."
git config --global user.name "$GITHUB_USERNAME"
read -p "Введите ваш email для Git: " GIT_EMAIL
git config --global user.email "$GIT_EMAIL"
git config --global credential.helper store

# Тестирование клонирования
log "Тестирование доступа к репозиторию..."
if [ -n "$GITHUB_TOKEN" ]; then
    TEST_URL="https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$GITHUB_REPO.git"
else
    TEST_URL="git@github.com:$GITHUB_USERNAME/$GITHUB_REPO.git"
fi

# Создание временной директории для теста
TEMP_DIR="/tmp/test_repo_$$"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

if git clone "$TEST_URL" . > /dev/null 2>&1; then
    log "Доступ к репозиторию успешен ✅"
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
else
    error "Не удалось получить доступ к репозиторию. Проверьте настройки."
fi

log "🎉 Настройка приватного репозитория завершена!"
echo -e "${GREEN}✅ Теперь вы можете использовать:${NC}"
echo -e "${YELLOW}  ./deploy.sh - для полного развертывания${NC}"
echo -e "${YELLOW}  ./quick-deploy.sh - для быстрого обновления${NC}"
