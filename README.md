# TeddyAI - Інтерактивна іграшка для дiтей

TeddyAI — на разі, це мультимодульний застосунок написаний на мові програмування Python з використанням Flask для бекенду та Flet для фронтенду, що забезпечує голосову взаємодiю дитини з іграшкою, фiльтрує небажанi запити та захищає користувачів через JWT авторизацiю.

## 📄 Основнi можливостi

* Синтез мовлення із GPT-відповідей (gTTS)
* Безпечне оброблення дитячих запитів (фільтр нецензурної лексики)
* Підтримка OpenAI API Key у кожного користувача
* JWT-авторизацiя (реєстрацiя/логін)
* Історія запитів
* Кроссплатформенність: Web, Android (через Flet)

---

## 🛠️ Встановлення

### ⚠️ Перед початком використання
```bash
# Linux or MacOS
chmod +x install.sh
./install.sh

# Windows
./install.bat
```
### 🌐 Backend (Flask)

```bash
.\venv\Scripts\activate  # Linux/macOS: source venv/bin/activate
python -m backend.app
```

### 🎨 Frontend (Flet)

```bash
.\venv\Scripts\activate  # Linux/macOS: source venv/bin/activate
python -m frontend.main
```

> **Примітка:** створіть файл `.env`, або ж створіть його за допомогою `install` файлу:

```
# === Environment File ===
# ⬇️ or other URL for server
SERVER_URL=http://127.0.0.1:5000
# ⬇️ node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
JWT_SECRET_KEY=your_very_secret_key
# ⬇️ python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_SECRET=your_encryption_secret_key_here
```

---

## 🌐 API Endpoint

### POST `/ask`

* **Headers:** `Authorization: Bearer <jwt>`
* **JSON:** `{ "question": "Чому існує людина?" }`
* **Response:** MP3 файл (audio/mpeg)

---

## 🔧 Структура проекту

```
└── Andromedov/AI-Toy-Remastered/
    ├── backend/
    │   ├── __init__.py
    │   ├── app.py
    │   ├── db_setup.py
    │   ├── encryption.py
    │   ├── models.py
    │   └── utils.py
    ├── frontend/
    │   ├── __init__.py
    │   ├── login_view.py
    │   ├── main.py
    │   └── teddy_view.py
    ├── .wordlist/
    │   └── banword_list.txt
    ├── .env
    ├── requirements.txt
    ├── README.md
    ├── install.bat
    └── install.sh

```

---

## 📈 План подальшого розвитку

* [x] Система авторизації користувачів
* [ ] ESP32 підтримка з WiFi-запитом до backend
* [ ] Збереження історії на сервері + відображення в інтерфейсі
* [ ] Мобільна версія як APK (Flet + Android Studio)
* [ ] Розширення TTS/ASR можливостей
* [x] Підключення до бази даних SQLite або MySQL (MariaDB)

---

## 🚀 Автор

**Yevhen «Andromedov» Harasymchuk** — кваліфікаційна робота, 2025

> Якщо виникли проблеми — звертайтайтесь у `issues`.
