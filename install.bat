@echo off

IF NOT EXIST requirements.txt (
    echo 📄 Файл requirements.txt не знайдено, створюємо...
    echo flask >> requirements.txt
    echo gtts >> requirements.txt
    echo openai >> requirements.txt
    echo python-dotenv >> requirements.txt
    echo better_profanity >> requirements.txt
)

IF NOT EXIST venv (
    echo 🔧 Створення віртуального середовища...
    python -m venv venv
)

call venv\Scripts\activate

echo 📦 Встановлення пакетів...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Готово!
pause
