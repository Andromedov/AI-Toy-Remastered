import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

# To use access token use this command and set it in .env
# node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

def hash_password(password: str) -> str:
    """Хешування пароля"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Перевірка пароля"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(identity: str) -> str:
    """Генерує JWT токен (24 години)"""
    return create_access_token(identity=identity, expires_delta=timedelta(days=1))
