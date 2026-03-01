"""
services/translator.py — Переклад тексту через Google Translate (googletrans).
Як запасний варіант — DeepL API (якщо є ключ).
"""
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class TranslatorService:
    """
    Обгортка над googletrans (безкоштовна) та DeepL (платна).
    Спочатку намагається використати DeepL, якщо є ключ.
    """

    def __init__(self, deepl_key: str = "", google_translate_key: str = ""):
        self._deepl_key = deepl_key
        self._google_key = google_translate_key

    async def translate(
        self,
        text: str,
        target_lang: str = "uk",
        source_lang: str = "auto",
    ) -> str:
        """
        Перекладає текст на цільову мову.
        :param text: вхідний текст
        :param target_lang: цільова мова ("uk", "en", тощо)
        :param source_lang: мова джерела ("auto" = автовизначення)
        :return: перекладений текст або оригінал при помилці
        """
        if not text or not text.strip():
            return text

        # Спочатку пробуємо DeepL якщо є ключ
        if self._deepl_key:
            result = await self._translate_deepl(text, target_lang)
            if result:
                return result

        # Якщо DeepL недоступний — використовуємо googletrans
        return await self._translate_google(text, target_lang, source_lang)

    async def _translate_deepl(self, text: str, target_lang: str) -> Optional[str]:
        """Переклад через DeepL REST API."""
        try:
            import aiohttp
            # DeepL використовує свої коди мов
            lang_map = {"uk": "UK", "en": "EN-US"}
            dl_lang = lang_map.get(target_lang, target_lang.upper())

            api_url = "https://api-free.deepl.com/v2/translate"
            headers = {"Authorization": f"DeepL-Auth-Key {self._deepl_key}"}
            payload = {"text": [text], "target_lang": dl_lang}

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    api_url, json=payload, headers=headers,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["translations"][0]["text"]
        except Exception as e:
            logger.warning(f"DeepL помилка: {e}")
        return None

    async def _translate_google(
        self, text: str, target_lang: str, source_lang: str
    ) -> str:
        """Переклад через googletrans (реверс-інжиніринг Google Translate)."""
        try:
            # Виконуємо в executor щоб не блокувати event loop
            from googletrans import Translator
            translator = Translator()
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: translator.translate(
                    text,
                    dest=target_lang,
                    src=source_lang if source_lang != "auto" else "auto",
                ),
            )
            return result.text
        except Exception as e:
            logger.error(f"googletrans помилка: {e}")
            return text  # Повертаємо оригінал при помилці

    async def translate_articles(
        self, articles: list, target_lang: str = "uk"
    ) -> list:
        """Перекладає заголовки новин."""
        if target_lang == "en":
            return articles  # Новини вже англійською

        translated = []
        for article in articles:
            new_article = article.copy()
            if article.get("title"):
                new_article["title"] = await self.translate(
                    article["title"], target_lang
                )
            if article.get("description"):
                new_article["description"] = await self.translate(
                    article["description"], target_lang
                )
            translated.append(new_article)
        return translated
