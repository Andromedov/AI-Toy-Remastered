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

### 🌐 Backend (Flask)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python ./app.py
```

### 🎨 Frontend (Flet)

```bash
cd frontend
pip install -r requirements.txt
flet run main.py -d
```

> **Примітка:** створіть файл `.env` у `frontend/` та `backend/`:

```
SERVER_URL=http://127.0.0.1:5000
JWT_SECRET=your_very_secret_key # Щоб створити ключ використайте наступну команду (необхідний NodeJS):
# node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
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
TeddyAI/
├── backend/
│   ├── app.py
│   ├── db.py
│   ├── models.py
│   └── auth.py
├── frontend/
│   ├── .config.json
│   ├── main.py
│   ├── teddy_view.py
│   └── login_view.py
├── .wordlist/
│   └── banword_list.txt
└── .env
```

---

## 📈 План подальшого розвитку

* [x] Система авторизації користувачів
* [ ] ESP32 підтримка з WiFi-запитом до backend
* [ ] Збереження історії на сервері + відображення в інтерфейсі
* [ ] Мобільна версія як APK (Flet + Android Studio)
* [ ] Розширення TTS/ASR можливостей
* [ ] Підключення до бази даних SQLite

---

## 🚀 Автор

**Yevhen «Andromedov» Harasymchuk** — дипломний проєкт, 2025

> Якщо виникли проблеми — звертайтайтесь у `issues`.
