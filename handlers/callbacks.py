"""
handlers/callbacks.py — Обробники inline-кнопок.
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import get_main_keyboard
from i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith("choose_loc:"))
async def callback_choose_location(query: CallbackQuery, state: FSMContext, db):
    """Вибір міста з кількох варіантів."""
    idx = int(query.data.split(":")[1])
    data = await state.get_data()
    lang = data.get("lang", "uk")
    locations = data.get("locations", [])

    if idx >= len(locations):
        await query.answer(get_text("error_try_again", lang))
        return

    loc = locations[idx]
    async with db.session() as session:
        repo = db.get_repository(session)
        await repo.create_or_update_user(
            telegram_id=query.from_user.id,
            city=loc["city"],
            country=loc["country"],
            country_code=loc["country_code"],
        )

    await state.clear()
    await query.message.edit_text(
        get_text("location_saved", lang).format(city=loc["city"], country=loc["country"]),
        parse_mode="HTML",
    )
    await query.message.answer("👇", reply_markup=get_main_keyboard(lang))
    await query.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("set_lang:"))
async def callback_set_language(query: CallbackQuery, db):
    """Зміна мови з налаштувань."""
    new_lang = query.data.split(":")[1]
    async with db.session() as session:
        repo = db.get_repository(session)
        await repo.create_or_update_user(
            telegram_id=query.from_user.id,
            language=new_lang,
        )

    await query.message.edit_text(
        get_text("language_changed", new_lang),
        parse_mode="HTML",
    )
    await query.message.answer("👇", reply_markup=get_main_keyboard(new_lang))
    await query.answer(get_text("done", new_lang))


@router.callback_query(lambda c: c.data == "clear_data")
async def callback_clear_data(query: CallbackQuery, db):
    """Видаляє дані користувача."""
    async with db.session() as session:
        repo = db.get_repository(session)
        deleted = await repo.delete_user_data(query.from_user.id)

    lang = "uk"
    msg = get_text("data_cleared", lang) if deleted else get_text("no_data_found", lang)
    await query.message.edit_text(msg)
    await query.answer()


@router.callback_query(lambda c: c.data == "cancel")
async def callback_cancel(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("❌ Скасовано.")
    await query.answer()