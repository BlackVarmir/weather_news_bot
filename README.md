# 🌤 Weather & News Telegram Bot

Повнофункціональний Telegram-бот на **Aiogram 3.x** з погодою, новинами, геолокацією та шифруванням даних.

---

## 📁 Структура проєкту

```
weather_news_bot/
├── main.py                  # Точка входу, реєстрація хендлерів
├── config.py                # Завантаження .env конфігурації
├── i18n.py                  # Багатомовні рядки (uk/en)
│
├── handlers/
│   ├── start.py             # /start, отримання геолокації
│   ├── weather.py           # /weather
│   ├── news.py              # /news
│   ├── settings.py          # /settings
│   └── callbacks.py         # Inline-кнопки
│
├── services/
│   ├── weather.py           # OpenWeatherMap API
│   ├── news.py              # NewsAPI
│   ├── translator.py        # Google Translate / DeepL
│   └── geo.py               # geopy (Nominatim geocoder)
│
├── database/
│   ├── models.py            # SQLAlchemy-моделі
│   ├── repository.py        # CRUD + шифрування
│   └── encryption.py        # Fernet (AES-128)
│
├── tests/
│   ├── test_encryption.py   # Unit-тести шифрування
│   └── test_services.py     # Unit-тести сервісів
│
├── .env.example             # Шаблон конфігурації
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## ⚙️ Функціонал

| Команда | Опис |
|---------|------|
| `/start` | Вітання, запит геолокації або міста |
| `/weather` | Поточна погода для вашого міста |
| `/news` | Топ-новини вашої країни (з перекладом) |
| `/settings` | Зміна міста, мови, видалення даних |

### Додаткові можливості
- 📍 **Геолокація** через Telegram або ввід міста текстом
- 🌍 **Визначення країни** через geopy (Nominatim / OpenStreetMap)
- 🔐 **Шифрування даних** — усі дані в БД зашифровані (Fernet/AES)
- 🗣 **Багатомовність** — українська та англійська
- 📰 **Переклад новин** через googletrans або DeepL
- 🏗 **Async архітектура** — aiogram 3, SQLAlchemy async, aiohttp

---

## 🚀 Запуск локально

### 1. Клонування та налаштування

```bash
git clone <your-repo-url>
cd weather_news_bot

# Створіть .env файл
cp .env.example .env
# Відредагуйте .env — заповніть всі ключі
```

### 2. Генерація Fernet-ключа

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Скопіюйте результат у FERNET_KEY у .env
```

### 3. Встановлення залежностей

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
# або: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 4. Запуск бота

```bash
python main.py
```

---

## 🐳 Запуск у Docker

### Локально через docker-compose

```bash
# Переконайтеся що .env заповнений
docker-compose up --build -d

# Перегляд логів
docker-compose logs -f bot

# Зупинка
docker-compose down
```

### Одиночний контейнер

```bash
docker build -t weather-bot .
docker run -d \
  --name weather-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  weather-bot
```

---

## ☁️ Розгортання на Railway

```bash
# Встановіть Railway CLI
npm install -g @railway/cli

# Логін та ініціалізація
railway login
railway init

# Встановіть змінні середовища
railway variables set BOT_TOKEN=... OPENWEATHER_KEY=... NEWS_KEY=... FERNET_KEY=...

# Deploy
railway up
```

> **Важливо для Railway:** змініть `DATABASE_URL` на PostgreSQL (надається Railway безкоштовно).

---

## ☁️ Розгортання на Google Cloud Run

```bash
# Збудуйте та завантажте образ
gcloud builds submit --tag gcr.io/YOUR_PROJECT/weather-bot

# Deploy
gcloud run deploy weather-bot \
  --image gcr.io/YOUR_PROJECT/weather-bot \
  --platform managed \
  --region europe-west1 \
  --set-env-vars BOT_TOKEN=...,OPENWEATHER_KEY=...,NEWS_KEY=...,FERNET_KEY=... \
  --no-allow-unauthenticated
```

> **Примітка:** Cloud Run краще підходить для webhook-режиму. Для polling використовуйте Cloud Run Jobs або звичайну VM.

---

## 🧪 Запуск тестів

```bash
pytest tests/ -v

# З покриттям
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

---

## 🔐 Безпека

- Токени зберігаються **тільки в .env** (не в коді)
- Дані в БД шифруються **Fernet (AES-128-CBC + HMAC-SHA256)**
- Команда `/settings` → "Видалити мої дані" — GDPR-compliant очищення
- `.env` додано в `.gitignore` та `.dockerignore`

---

## 📦 Отримання API ключів

| Сервіс | URL | Безкоштовний ліміт |
|--------|-----|--------------------|
| Telegram Bot | @BotFather | Безлімітно |
| OpenWeatherMap | openweathermap.org/api | 60 req/хв, 1M/місяць |
| NewsAPI | newsapi.org/register | 100 req/день |
| DeepL | deepl.com/pro-api | 500K символів/місяць |

---

## 🛠 Технології

- **aiogram 3.x** — асинхронний Telegram Bot Framework
- **SQLAlchemy 2.0 async** — ORM для бази даних
- **aiohttp** — асинхронні HTTP-запити
- **cryptography (Fernet)** — шифрування AES-128
- **geopy (Nominatim)** — геокодування через OpenStreetMap
- **googletrans** — безкоштовний переклад

---

## 👨‍💻 Автор

Розроблено як навчальний проєкт для демонстрації async Python архітектури, шифрування та інтеграції з зовнішніми API.
