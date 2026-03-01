"""
tests/test_services.py — Unit-тести для сервісів (мокування API).
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.weather import WeatherService
from services.news import NewsService
from services.geo import GeoService


# ── WeatherService ────────────────────────────────────────────────────────────

class TestWeatherService:
    def setup_method(self):
        self.service = WeatherService(api_key="test_key")

    def test_format_weather_ukrainian(self):
        """Перевіряє форматування погоди українською."""
        mock_data = {
            "name": "Kyiv",
            "sys": {"country": "UA"},
            "main": {
                "temp": 15.5,
                "feels_like": 13.0,
                "humidity": 70,
                "pressure": 1013,
            },
            "wind": {"speed": 5.0},
            "weather": [{"description": "ясно", "main": "Clear"}],
            "visibility": 10000,
        }
        result = self.service.format_weather(mock_data, lang="uk")
        assert "Kyiv" in result
        assert "15.5" in result
        assert "70%" in result

    def test_format_weather_english(self):
        """Перевіряє форматування погоди англійською."""
        mock_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {"temp": 10.0, "feels_like": 8.0, "humidity": 80, "pressure": 1005},
            "wind": {"speed": 7.0},
            "weather": [{"description": "cloudy", "main": "Clouds"}],
            "visibility": 8000,
        }
        result = self.service.format_weather(mock_data, lang="en")
        assert "Weather in London" in result
        assert "Temperature" in result

    @pytest.mark.asyncio
    async def test_get_weather_city_not_found(self):
        """404 від API → повертає None."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_resp = AsyncMock()
            mock_resp.status = 404
            mock_resp.raise_for_status = AsyncMock()
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_resp

            result = await self.service.get_weather("НеіснуючеМісто")
            assert result is None


# ── NewsService ───────────────────────────────────────────────────────────────

class TestNewsService:
    def setup_method(self):
        self.service = NewsService(api_key="test_key")

    def test_format_articles_empty(self):
        """Порожній список → повідомлення про відсутність новин."""
        result = self.service.format_articles([], lang="uk")
        assert "не знайдено" in result.lower() or "Новин" in result

    def test_format_articles_with_data(self):
        """Коректний список → форматований текст."""
        articles = [
            {
                "title": "Тестова новина",
                "source": {"name": "Test Source"},
                "url": "https://example.com",
                "publishedAt": "2025-01-15T10:00:00Z",
            }
        ]
        result = self.service.format_articles(articles, lang="uk")
        assert "Тестова новина" in result
        assert "Test Source" in result

    def test_supported_countries_includes_ukraine(self):
        """Перевіряє що Україна є в списку підтримуваних країн."""
        assert "ua" in self.service._supported_countries()


# ── i18n ─────────────────────────────────────────────────────────────────────

class TestI18n:
    def test_get_text_ukrainian(self):
        from i18n import get_text
        text = get_text("cancel", "uk")
        assert "Скасувати" in text

    def test_get_text_english(self):
        from i18n import get_text
        text = get_text("cancel", "en")
        assert "Cancel" in text

    def test_get_text_unknown_key(self):
        from i18n import get_text
        text = get_text("nonexistent_key_xyz", "uk")
        assert "nonexistent_key_xyz" in text  # Повертає [key]
