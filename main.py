"""
main.py — Головна точка входу Telegram-бота.
Реєстрація хендлерів, ініціалізація сервісів, запуск polling.
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
# Для продакшн: from aiogram.fsm.storage.redis import RedisStorage

from config import config
from database.encryption import Encryptor
from database.repository import DatabaseManager
from services.weather import WeatherService
from services.news import NewsService
from services.translator import TranslatorService
from services.geo import GeoService

# Хендлери
from handlers import start, weather, news, settings, callbacks, help

# ── Налаштування логування ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("🚀 Запуск бота...")

    # ── Ініціалізація шифрування та БД ──────────────────────────────────────
    encryptor = Encryptor(config.fernet_key)
    db_manager = DatabaseManager(config.database_url, encryptor)
    await db_manager.init_db()

    # ── Ініціалізація сервісів ───────────────────────────────────────────────
    weather_service = WeatherService(config.openweather_key)
    news_service = NewsService(config.news_key)
    translator = TranslatorService(
        deepl_key=config.deepl_key,
        google_translate_key=config.translate_key,
    )
    geo_service = GeoService()

    # ── Telegram Bot ─────────────────────────────────────────────────────────
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # FSM storage (для продакшн замініть на Redis)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # ── Реєстрація роутерів ──────────────────────────────────────────────────
    dp.include_router(start.router)
    dp.include_router(callbacks.router)
    dp.include_router(weather.router)
    dp.include_router(news.router)
    dp.include_router(settings.router)
    dp.include_router(help.router)

    # ── Middleware для ін'єкції залежностей ──────────────────────────────────
    # Передаємо сервіси через workflow_data
    dp.update.middleware(
        _DependencyMiddleware(
            db=db_manager,
            weather_service=weather_service,
            news_service=news_service,
            translator=translator,
            geo_service=geo_service,
        )
    )

    # ── Запуск ──────────────────────────────────────────────────────────────
    try:
        logger.info("✅ Бот запущено. Очікування повідомлень...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("🛑 Бот зупинено.")


# ── Middleware для ін'єкції залежностей ──────────────────────────────────────
from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class _DependencyMiddleware(BaseMiddleware):
    """
    Передає сервіси в хендлери через data-словник.
    Доступ у хендлері: async def cmd_foo(message, db, weather_service, ...)
    """

    def __init__(self, **services):
        self._services = services
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict,
    ) -> Any:
        data.update(self._services)
        return await handler(event, data)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Зупинено вручну (Ctrl+C).")