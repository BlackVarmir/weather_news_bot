"""
keyboards.py — Спільні клавіатури для бота.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard(lang: str = "uk") -> ReplyKeyboardMarkup:
    """
    Головна клавіатура після того як місто збережено.
    З'являється замість кнопок геолокації.
    """
    if lang == "uk":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🌤 Погода"),
                    KeyboardButton(text="📰 Новини"),
                ],
                [
                    KeyboardButton(text="⚙️ Налаштування"),
                    KeyboardButton(text="❓ Допомога"),
                ],
            ],
            resize_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🌤 Weather"),
                    KeyboardButton(text="📰 News"),
                ],
                [
                    KeyboardButton(text="⚙️ Settings"),
                    KeyboardButton(text="❓ Help"),
                ],
            ],
            resize_keyboard=True,
        )


def get_location_keyboard(lang: str = "uk") -> ReplyKeyboardMarkup:
    """Клавіатура для вибору способу введення локації."""
    if lang == "uk":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📍 Надіслати геопозицію",
                        request_location=True,
                    )
                ],
                [KeyboardButton(text="✏️ Ввести місто вручну")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📍 Share location",
                        request_location=True,
                    )
                ],
                [KeyboardButton(text="✏️ Enter city manually")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )