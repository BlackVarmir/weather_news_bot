"""
services/weather.py — Інтеграція з OpenWeatherMap API.
Документація: https://openweathermap.org/api
"""
import logging
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)

WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Іконки для кодів погоди (emoji)
WEATHER_ICONS = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}


class WeatherService:
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def get_weather(
        self, city: str, lang: str = "uk"
    ) -> Optional[dict]:
        """
        Отримує погоду для вказаного міста.
        :param city: назва міста
        :param lang: мова відповіді ("uk" або "en")
        :return: словник із даними погоди або None при помилці
        """
        # OWM підтримує uk для українського інтерфейсу
        owm_lang = "ua" if lang == "uk" else "en"

        params = {
            "q": city,
            "appid": self._api_key,
            "units": "metric",  # Цельсій
            "lang": owm_lang,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    WEATHER_BASE_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 404:
                        logger.warning(f"Місто не знайдено: {city}")
                        return None
                    if resp.status == 401:
                        logger.error("Невалідний OpenWeatherMap API ключ!")
                        return None
                    resp.raise_for_status()
                    return await resp.json()

        except aiohttp.ClientConnectorError:
            logger.error("Не вдалося підключитися до OpenWeatherMap.")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Помилка HTTP при запиті погоди: {e}")
            return None

    def format_weather(self, data: dict, lang: str = "uk") -> str:
        """Форматує відповідь API у зручний текст для Telegram."""
        city_name = data.get("name", "—")
        country = data.get("sys", {}).get("country", "")
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        description = data["weather"][0]["description"].capitalize()
        main_weather = data["weather"][0]["main"]
        icon = WEATHER_ICONS.get(main_weather, "🌡️")

        pressure_hpa = data["main"]["pressure"]
        visibility = data.get("visibility", 0) // 1000  # у км

        if lang == "uk":
            return (
                f"{icon} <b>Погода у {city_name}, {country}</b>\n\n"
                f"🌡 Температура: <b>{temp:.1f}°C</b> (відчувається як {feels_like:.1f}°C)\n"
                f"💧 Вологість: <b>{humidity}%</b>\n"
                f"💨 Вітер: <b>{wind_speed} м/с</b>\n"
                f"🔵 Тиск: <b>{pressure_hpa} гПа</b>\n"
                f"👁 Видимість: <b>{visibility} км</b>\n"
                f"📋 Опис: <i>{description}</i>"
            )
        else:
            return (
                f"{icon} <b>Weather in {city_name}, {country}</b>\n\n"
                f"🌡 Temperature: <b>{temp:.1f}°C</b> (feels like {feels_like:.1f}°C)\n"
                f"💧 Humidity: <b>{humidity}%</b>\n"
                f"💨 Wind: <b>{wind_speed} m/s</b>\n"
                f"🔵 Pressure: <b>{pressure_hpa} hPa</b>\n"
                f"👁 Visibility: <b>{visibility} km</b>\n"
                f"📋 Description: <i>{description}</i>"
            )
