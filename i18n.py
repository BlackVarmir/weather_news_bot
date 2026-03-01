"""
i18n.py — Багатомовні рядки інтерфейсу (українська та англійська).
"""

TRANSLATIONS = {
    # --- welcome back ---
    "welcome_back": {
        "uk": "👋 З поверненням, <b>{name}</b>!\n📍 Ваше місто: <b>{city}</b>",
        "en": "👋 Welcome back, <b>{name}</b>!\n📍 Your city: <b>{city}</b>",
    },
    "ask_location": {
        "uk": "📍 Надішліть геопозицію або введіть місто вручну:",
        "en": "📍 Share your location or enter a city manually:",
    },
    # --- /start ---
    "welcome": {
        "uk": (
            "👋 Привіт, <b>{name}</b>!\n\n"
            "Я — бот погоди та новин 🌤📰\n\n"
            "Надішліть геопозицію або введіть місто.\n"
            "Команда /help — довідка по боту."
        ),
        "en": (
            "👋 Hello, <b>{name}</b>!\n\n"
            "I'm a weather and news bot 🌤📰\n\n"
            "Share your location or enter a city.\n"
            "Use /help to see available commands."
        ),
    },
    "send_location": {
        "uk": "📍 Надіслати геопозицію",
        "en": "📍 Share location",
    },
    "enter_city_manually": {
        "uk": "✏️ Ввести місто вручну",
        "en": "✏️ Enter city manually",
    },
    "detecting_location": {
        "uk": "🔍 Визначаю ваше місцезнаходження...",
        "en": "🔍 Detecting your location...",
    },
    "location_error": {
        "uk": "❌ Не вдалося визначити місцезнаходження. Спробуйте ввести місто вручну.",
        "en": "❌ Failed to detect location. Try entering the city manually.",
    },
    "location_saved": {
        "uk": "✅ Збережено: <b>{city}, {country}</b>\n\nТепер ви можете використовувати /weather та /news.",
        "en": "✅ Saved: <b>{city}, {country}</b>\n\nNow you can use /weather and /news.",
    },
    "enter_city_prompt": {
        "uk": "✏️ Введіть назву міста:",
        "en": "✏️ Enter city name:",
    },
    "searching_city": {
        "uk": "🔍 Шукаю місто...",
        "en": "🔍 Searching city...",
    },
    "city_not_found": {
        "uk": "❌ Місто «<b>{city}</b>» не знайдено. Спробуйте ввести по-англійськи.",
        "en": "❌ City «<b>{city}</b>» not found. Try a different spelling.",
    },
    "multiple_cities": {
        "uk": "Знайдено кілька міст. Оберіть потрібне:",
        "en": "Multiple cities found. Please choose:",
    },

    # --- /weather ---
    "loading_weather": {
        "uk": "⏳ Завантажую погоду...",
        "en": "⏳ Loading weather...",
    },
    "no_city_set": {
        "uk": "❗ Спочатку вкажіть місто командою /start або /settings.",
        "en": "❗ Please set your city first using /start or /settings.",
    },
    "weather_error": {
        "uk": "❌ Не вдалося отримати погоду для <b>{city}</b>. Перевірте назву міста.",
        "en": "❌ Failed to get weather for <b>{city}</b>. Check the city name.",
    },

    # --- /news ---
    "loading_news": {
        "uk": "⏳ Завантажую новини...",
        "en": "⏳ Loading news...",
    },
    "news_api_error": {
        "uk": "❌ Сервіс новин тимчасово недоступний. Спробуйте пізніше.",
        "en": "❌ News service is temporarily unavailable. Try again later.",
    },
    "no_news_found": {
        "uk": "📭 Новин не знайдено для вашого регіону.",
        "en": "📭 No news found for your region.",
    },

    # --- /settings ---
    "settings_menu": {
        "uk": (
            "⚙️ <b>Налаштування</b>\n\n"
            "📍 Місто: <b>{city}</b>\n"
            "🌍 Країна: <b>{country}</b>\n"
            "🗣 Мова: <b>{lang}</b>"
        ),
        "en": (
            "⚙️ <b>Settings</b>\n\n"
            "📍 City: <b>{city}</b>\n"
            "🌍 Country: <b>{country}</b>\n"
            "🗣 Language: <b>{lang}</b>"
        ),
    },
    "settings_change_city": {
        "uk": "🏙 Змінити місто",
        "en": "🏙 Change city",
    },
    "settings_clear_data": {
        "uk": "🗑 Видалити мої дані",
        "en": "🗑 Delete my data",
    },
    "language_changed": {
        "uk": "✅ Мову змінено на <b>Українська</b>.",
        "en": "✅ Language changed to <b>English</b>.",
    },
    "data_cleared": {
        "uk": "✅ Ваші дані видалено з бази.",
        "en": "✅ Your data has been deleted.",
    },
    "no_data_found": {
        "uk": "ℹ️ Ваших даних не знайдено в базі.",
        "en": "ℹ️ No data found for your account.",
    },

    # --- Загальне ---
    "cancel": {
        "uk": "❌ Скасувати",
        "en": "❌ Cancel",
    },
    "help_text": {
        "uk": (
            "❓ <b>Довідка по боту</b>\n\n"
            "🌤 <b>Погода</b> — поточна погода у вашому місті\n"
            "📰 <b>Новини</b> — останні новини (10 штук, по 5 на сторінці)\n"
            "⚙️ <b>Налаштування</b> — змінити місто, мову або видалити дані\n\n"
            "<b>Команди:</b>\n"
            "/start — перезапустити бота\n"
            "/weather — погода\n"
            "/news — новини\n"
            "/settings — налаштування\n"
            "/help — ця довідка\n\n"
            "💡 Використовуйте кнопки внизу для швидкого доступу!"
        ),
        "en": (
            "❓ <b>Bot Help</b>\n\n"
            "🌤 <b>Weather</b> — current weather in your city\n"
            "📰 <b>News</b> — latest news (10 articles, 5 per page)\n"
            "⚙️ <b>Settings</b> — change city, language or delete data\n\n"
            "<b>Commands:</b>\n"
            "/start — restart bot\n"
            "/weather — weather\n"
            "/news — news\n"
            "/settings — settings\n"
            "/help — this help\n\n"
            "💡 Use the buttons below for quick access!"
        ),
    },
    "done": {
        "uk": "Готово!",
        "en": "Done!",
    },
    "error_try_again": {
        "uk": "Помилка. Спробуйте ще раз.",
        "en": "Error. Please try again.",
    },
}


def get_text(key: str, lang: str = "uk") -> str:
    """
    Повертає перекладений рядок за ключем та мовою.
    За замовчуванням — українська.
    """
    translations = TRANSLATIONS.get(key, {})
    return translations.get(lang) or translations.get("uk") or f"[{key}]"