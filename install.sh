#!/bin/bash

if [ ! -d "venv" ]; then
  echo "🔧 Створення віртуального середовища..."
  python3 -m venv venv
fi

if [ ! -f ".env" ]; then
  echo "⚙️ Creating .env file..."
  cat <<EOL > .env
# === TeddyAI Environment ===
# ⬇️ or other URL for server
SERVER_URL=http://127.0.0.1:5000
# ⬇️ node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
JWT_SECRET_KEY=your_super_secret_key_here
# ⬇️ python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_SECRET=your_encryption_secret_key_here
EOL
  echo "✅ .env created — edit it to set your keys!"
fi

source venv/bin/activate

echo "📦 Встановлення пакетів..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Готово!"
