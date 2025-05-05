#!/bin/bash

echo "🔧 Створення віртуального середовища..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Встановлення пакетів..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Готово!"
