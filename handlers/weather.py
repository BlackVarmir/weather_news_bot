"""
handlers/weather.py — Обробник кнопки/команди Погода.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from services.weather import WeatherService
from i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("weather"))
@router.message(F.text.in_(["🌤 Погода", "🌤 Weather"]))
async def cmd_weather(message: Message, db, weather_service: WeatherService):
    async with db.session() as session:
        repo = db.get_repository(session)
        user_data = await repo.get_decrypted_data(message.from_user.id)

    if not user_data or not user_data.get("city"):
        lang = user_data.get("language", "uk") if user_data else "uk"
        await message.answer(get_text("no_city_set", lang))
        return

    city = user_data["city"]
    lang = user_data.get("language", "uk")

    loading_msg = await message.answer(get_text("loading_weather", lang))
    weather_data = await weather_service.get_weather(city, lang)
    await loading_msg.delete()

    if not weather_data:
        await message.answer(get_text("weather_error", lang).format(city=city), parse_mode="HTML")
        return

    text = weather_service.format_weather(weather_data, lang)
    await message.answer(text, parse_mode="HTML")