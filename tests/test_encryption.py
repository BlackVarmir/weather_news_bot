"""
tests/test_encryption.py — Unit-тести для модуля шифрування.
Запуск: pytest tests/
"""
import pytest
from cryptography.fernet import Fernet
from database.encryption import Encryptor


@pytest.fixture
def encryptor():
    """Фікстура: новий Encryptor зі згенерованим ключем."""
    key = Fernet.generate_key().decode()
    return Encryptor(key)


def test_encrypt_decrypt_roundtrip(encryptor):
    """Шифрування → дешифрування повертає оригінал."""
    plaintext = "Чернівці"
    ciphertext = encryptor.encrypt(plaintext)
    assert ciphertext != plaintext  # зашифровано
    assert encryptor.decrypt(ciphertext) == plaintext


def test_encrypt_empty_string(encryptor):
    """Порожній рядок залишається порожнім."""
    assert encryptor.encrypt("") == ""
    assert encryptor.decrypt("") == ""


def test_different_ciphertexts(encryptor):
    """Кожне шифрування дає різний результат (Fernet включає IV)."""
    text = "Kyiv"
    ct1 = encryptor.encrypt(text)
    ct2 = encryptor.encrypt(text)
    assert ct1 != ct2  # різні IV
    assert encryptor.decrypt(ct1) == encryptor.decrypt(ct2) == text


def test_invalid_key_raises():
    """Невалідний ключ викидає виняток."""
    with pytest.raises(Exception):
        Encryptor("не_валідний_ключ")


def test_tampered_ciphertext_returns_empty(encryptor):
    """Пошкоджений шифртекст повертає порожній рядок."""
    ct = encryptor.encrypt("secret")
    tampered = ct[:-10] + "XXXXXXXXXX"
    result = encryptor.decrypt(tampered)
    assert result == ""


def test_generate_key():
    """generate_key() повертає валідний Fernet-ключ."""
    key = Encryptor.generate_key()
    enc = Encryptor(key)
    assert enc.decrypt(enc.encrypt("test")) == "test"


def test_unicode_support(encryptor):
    """Підтримка Unicode (кирилиця, емодзі)."""
    texts = ["Привіт 🌍", "Чернівецький університет", "температура -15°C"]
    for text in texts:
        assert encryptor.decrypt(encryptor.encrypt(text)) == text
