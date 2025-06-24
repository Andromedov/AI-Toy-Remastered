from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

ENCRYPTION_SECRET = os.getenv("ENCRYPTION_SECRET")
if not ENCRYPTION_SECRET:
    raise ValueError("❌ Не знайдено ENCRYPTION_SECRET у .env файлі!")

fernet = Fernet(ENCRYPTION_SECRET.encode())

def encrypt_api_key(key: str) -> str:
    """Шифрує API ключ"""
    return fernet.encrypt(key.encode()).decode()

def decrypt_api_key(token: str) -> str:
    """Дешифрує API ключ"""
    return fernet.decrypt(token.encode()).decode()
