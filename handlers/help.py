"""
handlers/help.py — Команда /help.
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from i18n import get_text

router = Router()


@router.message(Command("help"))
@router.message(F.text.in_(["❓ Допомога", "❓ Help"]))
async def cmd_help(message: Message, db):
    try:
        async with db.session() as session:
            repo = db.get_repository(session)
            user_data = await repo.get_decrypted_data(message.from_user.id)
        lang = user_data.get("language", "uk") if user_data else "uk"
    except Exception:
        lang = "uk"

    await message.answer(get_text("help_text", lang), parse_mode="HTML")