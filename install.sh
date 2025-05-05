#!/bin/bash

# Створення requirements.txt, якщо його нема
if [ ! -f "requirements.txt" ]; then
  echo "📄 Файл requirements.txt не знайдено, створюємо..."
  cat <<EOL > requirements.txt
flask
gtts
openai
python-dotenv
better_profanity
EOL
fi

# Створення віртуального середовища, якщо його нема
if [ ! -d "venv" ]; then
  echo "🔧 Створення віртуального середовища..."
  python3 -m venv venv
fi

# Активація середовища
source venv/bin/activate

# Встановлення залежностей
echo "📦 Встановлення пакетів..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Готово!"
