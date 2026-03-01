"""
services/news.py — Інтеграція з NewsAPI.
Документація: https://newsapi.org/docs
"""
import logging
from typing import Optional, List
import aiohttp

logger = logging.getLogger(__name__)

NEWS_BASE_URL = "https://newsapi.org/v2/top-headlines"
NEWS_EVERYTHING_URL = "https://newsapi.org/v2/everything"


class NewsService:
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def get_news(
        self,
        country_code: str = None,
        query: str = None,
        page_size: int = 5,
    ) -> Optional[List[dict]]:
        """
        Отримує новини за кодом країни або пошуковим запитом.
        :param country_code: ISO 3166-1 alpha-2 (наприклад 'ua', 'us')
        :param query: пошуковий запит
        :param page_size: кількість новин
        :return: список статей або None при помилці
        """
        params = {
            "apiKey": self._api_key,
            "pageSize": page_size,
        }

        # Визначаємо endpoint та параметри
        if country_code and country_code.lower() in self._supported_countries():
            url = NEWS_BASE_URL
            params["country"] = country_code.lower()
        elif query:
            url = NEWS_EVERYTHING_URL
            params["q"] = query
            params["sortBy"] = "publishedAt"
        else:
            # Глобальні новини за замовчуванням
            url = NEWS_BASE_URL
            params["country"] = "us"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 401:
                        logger.error("Невалідний NewsAPI ключ!")
                        return None
                    if resp.status == 429:
                        logger.warning("Перевищено ліміт запитів NewsAPI.")
                        return None
                    resp.raise_for_status()
                    data = await resp.json()
                    articles = data.get("articles", [])
                    # Фільтруємо порожні статті
                    return [a for a in articles if a.get("title") and a["title"] != "[Removed]"]

        except aiohttp.ClientConnectorError:
            logger.error("Не вдалося підключитися до NewsAPI.")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Помилка HTTP при запиті новин: {e}")
            return None

    @staticmethod
    def _supported_countries() -> set:
        """NewsAPI підтримує обмежений набір країн для top-headlines."""
        return {
            "ae", "ar", "at", "au", "be", "bg", "br", "ca", "ch", "cn",
            "co", "cu", "cz", "de", "eg", "fr", "gb", "gr", "hk", "hu",
            "id", "ie", "il", "in", "it", "jp", "kr", "lt", "lv", "ma",
            "mx", "my", "ng", "nl", "no", "nz", "ph", "pl", "pt", "ro",
            "rs", "ru", "sa", "se", "sg", "si", "sk", "th", "tr", "tw",
            "ua", "us", "ve", "za",
        }

    @staticmethod
    def format_articles(articles: List[dict], lang: str = "uk") -> str:
        """Форматує список статей у Telegram-повідомлення."""
        if not articles:
            if lang == "uk":
                return "📭 Новин не знайдено."
            return "📭 No news found."

        lines = []
        header = "📰 <b>Останні новини</b>\n" if lang == "uk" else "📰 <b>Latest News</b>\n"
        lines.append(header)

        for i, article in enumerate(articles, 1):
            title = article.get("title", "—")
            source = article.get("source", {}).get("name", "—")
            url = article.get("url", "")
            published = article.get("publishedAt", "")[:10]  # тільки дата

            lines.append(f"{i}. <a href='{url}'>{title}</a>")
            lines.append(f"   📌 {source} · {published}\n")

        return "\n".join(lines)
