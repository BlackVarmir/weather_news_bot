"""
handlers/settings.py — Команда /settings для налаштування бота.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


class SettingsStates(StatesGroup):
    waiting_for_new_city = State()


def settings_keyboard(lang: str = "uk") -> InlineKeyboardMarkup:
    """Клавіатура налаштувань."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("settings_change_city", lang),
                    callback_data="settings:change_city",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇦 Українська",
                    callback_data="set_lang:uk",
                ),
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data="set_lang:en",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text("settings_clear_data", lang),
                    callback_data="clear_data",
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_text("cancel", lang),
                    callback_data="cancel",
                )
            ],
        ]
    )


@router.message(Command("settings"))
@router.message(F.text.in_(["⚙️ Налаштування", "⚙️ Settings"]))
async def cmd_settings(message: Message, db):
    """Показує меню налаштувань."""
    async with db.session() as session:
        repo = db.get_repository(session)
        user_data = await repo.get_decrypted_data(message.from_user.id)

    lang = user_data.get("language", "uk") if user_data else "uk"
    city = user_data.get("city", "—") if user_data else "—"
    country = user_data.get("country", "—") if user_data else "—"

    text = get_text("settings_menu", lang).format(
        city=city,
        country=country,
        lang="🇺🇦 Українська" if lang == "uk" else "🇬🇧 English",
    )

    await message.answer(
        text,
        reply_markup=settings_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(lambda c: c.data == "settings:change_city")
async def callback_change_city(query: CallbackQuery, state: FSMContext, db):
    """Ініціює зміну міста."""
    async with db.session() as session:
        repo = db.get_repository(session)
        user_data = await repo.get_decrypted_data(query.from_user.id)
    lang = user_data.get("language", "uk") if user_data else "uk"

    await query.message.edit_text(get_text("enter_city_prompt", lang))
    await state.set_state(SettingsStates.waiting_for_new_city)
    await state.update_data(lang=lang)
    await query.answer()


@router.message(SettingsStates.waiting_for_new_city, F.text)
async def handle_new_city(
    message: Message, state: FSMContext, db
):
    """Зберігає нове місто."""
    from services.geo import GeoService
    data = await state.get_data()
    lang = data.get("lang", "uk")
    city_input = message.text.strip()

    geo = GeoService()
    locations = await geo.get_location_by_city(city_input)

    if not locations:
        await message.answer(get_text("city_not_found", lang).format(city=city_input))
        return

    loc = locations[0]
    async with db.session() as session:
        repo = db.get_repository(session)
        await repo.create_or_update_user(
            telegram_id=message.from_user.id,
            city=loc.city,
            country=loc.country,
            country_code=loc.country_code,
        )

    await message.answer(
        get_text("location_saved", lang).format(city=loc.city, country=loc.country),
        parse_mode="HTML",
    )
    await state.clear()