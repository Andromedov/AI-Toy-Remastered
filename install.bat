@echo off

IF NOT EXIST venv (
    echo 🔧 Створення віртуального середовища...
    python -m venv venv
)

call venv\Scripts\activate

IF NOT EXIST .env (
    echo Creating .env file...
    echo '# === TeddyAI Environment ===' >> .env
    echo '# ⬇️ or other URL for server' >> .env
    echo 'SERVER_URL=http://127.0.0.1:5000' >> .env
    echo '# ⬇️ node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"' >> .env
    echo 'JWT_SECRET_KEY=your_super_secret_key_here' >> .env
    echo '# ⬇️ python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"' >> .env
    echo 'ENCRYPTION_SECRET=your_encryption_secret_key_here' >> .env
    echo ✅ .env created — edit it to set your keys!
)

echo 📦 Встановлення пакетів...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Готово!
pause
