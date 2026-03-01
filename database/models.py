"""
database/models.py — SQLAlchemy-моделі бази даних.
Усі чутливі поля зберігаються в зашифрованому вигляді.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Модель користувача Telegram-бота.
    Поля city_enc, country_enc — зашифровані значення.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)

    # Зашифровані дані (AES/Fernet)
    city_enc = Column(String, nullable=True)       # зашифроване місто
    country_enc = Column(String, nullable=True)    # зашифрована країна
    country_code_enc = Column(String, nullable=True)  # ISO код країни

    # Мова (не є конфіденційною, але теж шифруємо для однорідності)
    language = Column(String(5), default="uk")     # "uk" або "en"

    # Службові поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User telegram_id={self.telegram_id} lang={self.language}>"
