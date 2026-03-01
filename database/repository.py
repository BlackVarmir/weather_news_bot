"""
database/repository.py — CRUD-операції з базою даних.
Шифрування відбувається тут, перед збереженням.
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from database.models import Base, User
from database.encryption import Encryptor

logger = logging.getLogger(__name__)


class UserRepository:
    """Репозиторій для роботи з таблицею users."""

    def __init__(self, session: AsyncSession, encryptor: Encryptor):
        self._session = session
        self._enc = encryptor

    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Повертає користувача за telegram_id або None."""
        result = await self._session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update_user(
        self,
        telegram_id: int,
        city: str = None,
        country: str = None,
        country_code: str = None,
        language: str = None,
    ) -> User:
        """
        Створює нового або оновлює існуючого користувача.
        Чутливі дані шифруються перед збереженням.
        """
        user = await self.get_user(telegram_id)

        if not user:
            user = User(telegram_id=telegram_id)
            self._session.add(user)
            logger.info(f"Створено нового користувача: {telegram_id}")

        # Шифруємо перед збереженням
        if city is not None:
            user.city_enc = self._enc.encrypt(city)
        if country is not None:
            user.country_enc = self._enc.encrypt(country)
        if country_code is not None:
            user.country_code_enc = self._enc.encrypt(country_code)
        if language is not None:
            user.language = language

        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def get_decrypted_data(self, telegram_id: int) -> dict:
        """
        Повертає розшифровані дані користувача.
        """
        user = await self.get_user(telegram_id)
        if not user:
            return {}
        return {
            "telegram_id": user.telegram_id,
            "city": self._enc.decrypt(user.city_enc or ""),
            "country": self._enc.decrypt(user.country_enc or ""),
            "country_code": self._enc.decrypt(user.country_code_enc or ""),
            "language": user.language,
        }

    async def delete_user_data(self, telegram_id: int) -> bool:
        """Очищає дані користувача (GDPR-compliant)."""
        user = await self.get_user(telegram_id)
        if not user:
            return False
        user.city_enc = None
        user.country_enc = None
        user.country_code_enc = None
        await self._session.commit()
        logger.info(f"Дані користувача {telegram_id} видалено.")
        return True


class DatabaseManager:
    """Менеджер підключень до БД."""

    def __init__(self, database_url: str, encryptor: Encryptor):
        self._engine = create_async_engine(
            database_url,
            echo=False,  # Встановіть True для дебагу SQL
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        self._encryptor = encryptor

    async def init_db(self):
        """Створює таблиці якщо їх немає."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ База даних ініціалізована.")

    def get_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session, self._encryptor)

    async def get_session(self) -> AsyncSession:
        """Контекстний менеджер для отримання сесії."""
        return self._session_factory()

    # Використання: async with db.session() as session:
    def session(self):
        return self._session_factory()
