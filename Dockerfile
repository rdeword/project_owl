FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app

# Копирование зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY backend/ ./backend/
COPY webapp/ ./webapp/

# Создание директории для логов
RUN mkdir -p /app/logs && chown -R app:app /app

# Переключение на пользователя app
USER app

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["python", "backend/main.py"]
