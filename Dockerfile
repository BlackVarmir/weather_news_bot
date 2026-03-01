# ══════════════════════════════════════════════════════════════
#  Dockerfile — Мінімальний образ для продакшн
# ══════════════════════════════════════════════════════════════

# Базовий образ: slim Python 3.13
FROM python:3.13-slim

# Метадані
LABEL maintainer="blackvarmir@gmail.com"
LABEL description="Weather & News Telegram Bot"

# Робоча директорія всередині контейнера
WORKDIR /app

# Копіюємо залежності першими (для кешування шарів)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо решту коду
COPY . .

# Не запускаємо від root
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Директорія для SQLite БД (монтується як volume)
RUN mkdir -p /app/data

# Змінна середовища для шляху до БД у контейнері
ENV DATABASE_URL=sqlite+aiosqlite:///data/bot_data.db

# Порт не потрібен (бот використовує polling, не webhook)
# EXPOSE 8080  # розкоментуйте якщо перейдете на webhook

# Точка входу
CMD ["python", "main.py"]
