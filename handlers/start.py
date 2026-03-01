"""
handlers/start.py — /start з вибором мови → локація → головне меню.
"""
import logging
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.geo import GeoService
from keyboards import get_location_keyboard, get_main_keyboard
from i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


class StartStates(StatesGroup):
    choosing_language = State()   # крок 1: вибір мови
    waiting_for_city = State()    # крок 2: місто/геопозиція
    choosing_location = State()   # крок 3: вибір з кількох міст


def lang_keyboard() -> InlineKeyboardMarkup:
    """Inline-кнопки вибору мови при старті."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇦 Українська", callback_data="start_lang:uk"),
        InlineKeyboardButton(text="🇬🇧 English",    callback_data="start_lang:en"),
    ]])


# ── /start ────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db):
    await state.clear()

    # Якщо користувач вже є в БД — одразу показуємо головне меню
    user_data = await _get_user_data(message.from_user.id, db)
    if user_data and user_data.get("city"):
        lang = user_data.get("language", "uk")
        await message.answer(
            get_text("welcome_back", lang).format(
                name=message.from_user.first_name,
                city=user_data["city"],
            ),
            reply_markup=get_main_keyboard(lang),
            parse_mode="HTML",
        )
        return

    # Новий користувач — спочатку вибір мови
    await message.answer(
        "🌍 <b>Оберіть мову / Choose language:</b>",
        reply_markup=lang_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(StartStates.choosing_language)


# ── Вибір мови ────────────────────────────────────────────────────────────────

@router.callback_query(
    StartStates.choosing_language,
    lambda c: c.data and c.data.startswith("start_lang:")
)
async def callback_start_lang(query: CallbackQuery, state: FSMContext, db):
    lang = query.data.split(":")[1]

    # Зберігаємо мову в БД одразу
    async with db.session() as session:
        repo = db.get_repository(session)
        await repo.create_or_update_user(
            telegram_id=query.from_user.id,
            language=lang,
        )

    await state.update_data(lang=lang)
    await state.set_state(StartStates.waiting_for_city)

    await query.message.edit_text(
        get_text("welcome", lang).format(name=query.from_user.first_name),
        parse_mode="HTML",
    )
    await query.message.answer(
        get_text("ask_location", lang),
        reply_markup=get_location_keyboard(lang),
    )
    await query.answer()


# ── Геопозиція ────────────────────────────────────────────────────────────────

@router.message(StartStates.waiting_for_city, F.location)
async def handle_location(message: Message, state: FSMContext, db, geo_service: GeoService):
    data = await state.get_data()
    lang = data.get("lang", "uk")

    await message.answer(get_text("detecting_location", lang), reply_markup=ReplyKeyboardRemove())

    location = await geo_service.get_location_by_coords(
        message.location.latitude, message.location.longitude
    )

    if not location:
        await message.answer(get_text("location_error", lang))
        return

    async with db.session() as session:
        repo = db.get_repository(session)
        await repo.create_or_update_user(
            telegram_id=message.from_user.id,
            city=location.city,
            country=location.country,
            country_code=location.country_code,
        )

    await state.clear()
    await message.answer(
        get_text("location_saved", lang).format(city=location.city, country=location.country),
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML",
    )


# ── Кнопка "Ввести вручну" ────────────────────────────────────────────────────

@router.message(
    StartStates.waiting_for_city,
    F.text.in_(["✏️ Ввести місто вручну", "✏️ Enter city manually"]),
)
async def ask_city_manually(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uk")
    await message.answer(
        get_text("enter_city_prompt", lang),
        reply_markup=ReplyKeyboardRemove(),
    )


# ── Введення міста текстом ────────────────────────────────────────────────────

@router.message(StartStates.waiting_for_city, F.text)
async def handle_city_text(message: Message, state: FSMContext, db, geo_service: GeoService):
    data = await state.get_data()
    lang = data.get("lang", "uk")
    city_input = message.text.strip()

    await message.answer(get_text("searching_city", lang))
    locations = await geo_service.get_location_by_city(city_input)

    if not locations:
        await message.answer(get_text("city_not_found", lang).format(city=city_input))
        return

    if len(locations) == 1:
        await _save_and_show_main(message, state, db, locations[0], lang)
    else:
        buttons = [
            [InlineKeyboardButton(
                text=f"📍 {loc.city}, {loc.country}",
                callback_data=f"choose_loc:{i}",
            )]
            for i, loc in enumerate(locations[:5])
        ]
        await state.update_data(locations=[
            {"city": l.city, "country": l.country, "country_code": l.country_code}
            for l in locations
        ])
        await message.answer(
            get_text("multiple_cities", lang),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        await state.set_state(StartStates.choosing_location)


# ── Допоміжні функції ─────────────────────────────────────────────────────────

async def _save_and_show_main(message, state, db, loc, lang):
    async with db.session() as session:
        repo = db.get_repository(session)
        await repo.create_or_update_user(
            telegram_id=message.from_user.id,
            city=loc.city,
            country=loc.country,
            country_code=loc.country_code,
        )
    await state.clear()
    await message.answer(
        get_text("location_saved", lang).format(city=loc.city, country=loc.country),
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML",
    )


async def _get_user_data(telegram_id: int, db) -> dict:
    try:
        async with db.session() as session:
            repo = db.get_repository(session)
            return await repo.get_decrypted_data(telegram_id)
    except Exception:
        return {}