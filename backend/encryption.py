from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv("../.env")

FERNET_SECRET = os.getenv("ENCRYPTION_SECRET")
if not FERNET_SECRET:
    raise ValueError("❌ Не знайдено FERNET_SECRET у .env файлі!")

fernet = Fernet(FERNET_SECRET.encode())

def encrypt_api_key(key: str) -> str:
    """Шифрує API ключ"""
    return fernet.encrypt(key.encode()).decode()

def decrypt_api_key(token: str) -> str:
    """Дешифрує API ключ"""
    return fernet.decrypt(token.encode()).decode()
