@echo off

echo 🔧 Створення віртуального середовища...
python -m venv venv
call venv\Scripts\activate

echo 📦 Встановлення пакетів...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Готово!
pause
