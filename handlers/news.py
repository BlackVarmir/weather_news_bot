"""
handlers/news.py — Обробник кнопки/команди Новини з пагінацією.
10 новин по 5 на сторінці, навігація стрілками ◀️ ▶️
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from services.news import NewsService
from services.translator import TranslatorService
from i18n import get_text

logger = logging.getLogger(__name__)
router = Router()

PAGE_SIZE = 5  # новин на сторінці
TOTAL_NEWS = 10  # всього завантажуємо


def build_news_keyboard(articles: list, page: int, lang: str) -> tuple[str, InlineKeyboardMarkup]:
    """
    Формує текст сторінки та клавіатуру з пагінацією.
    Повертає (текст, клавіатура).
    """
    total_pages = (len(articles) + PAGE_SIZE - 1) // PAGE_SIZE
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_articles = articles[start:end]

    # Формуємо текст
    header = "📰 <b>Останні новини</b>" if lang == "uk" else "📰 <b>Latest News</b>"
    page_info = f"  <i>({page + 1}/{total_pages})</i>"
    lines = [header + page_info + "\n"]

    for i, article in enumerate(page_articles, start + 1):
        title = article.get("title", "—")
        source = article.get("source", {}).get("name", "—")
        url = article.get("url", "")
        date = article.get("publishedAt", "")[:10]
        lines.append(f"{i}. <a href='{url}'>{title}</a>")
        lines.append(f"   📌 {source} · {date}\n")

    text = "\n".join(lines)

    # Кнопки пагінації
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"news_page:{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"news_page:{page + 1}"))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[nav_buttons] if nav_buttons else [])
    return text, keyboard


async def fetch_articles(news_service, translator, country_code, city, lang):
    """Завантажує новини з fallback-логікою."""
    articles = None

    if country_code:
        articles = await news_service.get_news(country_code=country_code, page_size=TOTAL_NEWS)

    if not articles and city:
        articles = await news_service.get_news(query=city, page_size=TOTAL_NEWS)

    if not articles:
        articles = await news_service.get_news(query="world news", page_size=TOTAL_NEWS)

    if articles and lang == "uk":
        articles = await translator.translate_articles(articles, target_lang="uk")

    return articles or []


@router.message(Command("news"))
@router.message(F.text.in_(["📰 Новини", "📰 News"]))
async def cmd_news(message: Message, db, news_service: NewsService, translator: TranslatorService):
    async with db.session() as session:
        repo = db.get_repository(session)
        user_data = await repo.get_decrypted_data(message.from_user.id)

    if not user_data:
        await message.answer(get_text("no_city_set", "uk"))
        return

    lang = user_data.get("language", "uk")
    country_code = user_data.get("country_code", "")
    city = user_data.get("city", "")

    loading_msg = await message.answer(get_text("loading_news", lang))

    articles = await fetch_articles(news_service, translator, country_code, city, lang)

    await loading_msg.delete()

    if not articles:
        await message.answer(get_text("no_news_found", lang))
        return

    # Зберігаємо статті у FSM не потрібно — передаємо через callback_data індекс
    # Зберігаємо в bot_data через dispatcher (простіший підхід — окремий кеш)
    # Використовуємо глобальний кеш по telegram_id
    _news_cache[message.from_user.id] = articles

    text, keyboard = build_news_keyboard(articles, page=0, lang=lang)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML",
                         disable_web_page_preview=True)


@router.callback_query(lambda c: c.data and c.data.startswith("news_page:"))
async def callback_news_page(query: CallbackQuery, db):
    """Перегортає сторінки новин."""
    page = int(query.data.split(":")[1])

    async with db.session() as session:
        repo = db.get_repository(session)
        user_data = await repo.get_decrypted_data(query.from_user.id)

    lang = user_data.get("language", "uk") if user_data else "uk"

    articles = _news_cache.get(query.from_user.id, [])
    if not articles:
        await query.answer("Оновіть новини — натисніть 📰 Новини знову." if lang == "uk"
                           else "Please refresh news — tap 📰 News again.")
        return

    text, keyboard = build_news_keyboard(articles, page=page, lang=lang)

    await query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML",
                                  disable_web_page_preview=True)
    await query.answer()


# Простий in-memory кеш новин (очищається при перезапуску бота)
# Для продакшн — замінити на Redis або FSM-storage
_news_cache: dict[int, list] = {}