"""
config.py — Завантаження конфігурації з .env файлу.
Усі секрети зберігаються у змінних середовища.
"""
import os
import sys
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Завантажуємо .env якщо він існує
if not load_dotenv():
    print("⚠️  Файл .env не знайдено! Переконайтеся, що він існує або змінні середовища задані вручну.")

logger = logging.getLogger(__name__)


@dataclass
class Config:
    # Telegram
    bot_token: str

    # OpenWeatherMap
    openweather_key: str

    # NewsAPI
    news_key: str

    # Google Translate (необов'язково — якщо є)
    translate_key: str

    # Fernet-ключ для шифрування БД
    fernet_key: str

    # База даних
    database_url: str

    # DeepL (опціонально)
    deepl_key: str = ""


def load_config() -> Config:
    """Завантажує конфіг і перевіряє обов'язкові поля."""
    required = {
        "BOT_TOKEN": os.getenv("BOT_TOKEN"),
        "OPENWEATHER_KEY": os.getenv("OPENWEATHER_KEY"),
        "NEWS_KEY": os.getenv("NEWS_KEY"),
        "FERNET_KEY": os.getenv("FERNET_KEY"),
    }

    missing = [k for k, v in required.items() if not v]
    if missing:
        logger.critical(f"❌ Відсутні обов'язкові змінні середовища: {', '.join(missing)}")
        sys.exit(1)

    return Config(
        bot_token=required["BOT_TOKEN"],
        openweather_key=required["OPENWEATHER_KEY"],
        news_key=required["NEWS_KEY"],
        translate_key=os.getenv("TRANSLATE_KEY", ""),
        fernet_key=required["FERNET_KEY"],
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot_data.db"),
        deepl_key=os.getenv("DEEPL_KEY", ""),
    )


# Глобальний інстанс конфігу
config = load_config()
