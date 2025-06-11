from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gtts import gTTS
from better_profanity import profanity
from dotenv import load_dotenv, find_dotenv
from backend.encryption import encrypt_api_key, decrypt_api_key
from backend.models import Base, User, MessageHistory
from backend.utils import hash_password, check_password
from datetime import timedelta
import openai
import os
import uuid

# ========== Settings ==========
load_dotenv(find_dotenv())

app = Flask(__name__)
CORS(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "30 per minute"])

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=30) - For testing
jwt = JWTManager(app)

# Connection to SQLite
DATABASE_URL = "sqlite:///backend/users.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

banwords_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.wordlist', 'banword_list.txt'))
if os.path.exists(banwords_path):
    profanity.load_censor_words_from_file(banwords_path)
else:
    print(f"Banword list is not found at {banwords_path}")

# ========== DB Stuff ==========

@app.route("/save_api_key", methods=["POST"])
@jwt_required()
def save_api_key():
    email = get_jwt_identity()
    data = request.get_json()
    api_key = data.get("api_key", "").strip()

    if not api_key:
        return jsonify({"error": "Порожній API ключ"}), 400

    encrypted = encrypt_api_key(api_key)
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if user:
        user.api_key_encrypted = encrypted
        session.commit()
    session.close()

    return jsonify({"message": "Ключ збережено"}), 200

@app.route("/save_wifi", methods=["POST"])
@jwt_required()
def save_wifi():
    email = get_jwt_identity()
    data = request.get_json()
    ssid = data.get("ssid", "").strip()
    password = data.get("password", "").strip()

    if not ssid or not password:
        return jsonify({"error": "SSID і пароль обов’язкові"}), 400

    encrypted_ssid = encrypt_api_key(ssid)
    encrypted_password = encrypt_api_key(password)

    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if user:
        user.wifi_ssid_encrypted = encrypted_ssid
        user.wifi_password_encrypted = encrypted_password
        session.commit()
    session.close()

    return jsonify({"message": "WiFi налаштування збережено"}), 200

@app.route("/get_credentials", methods=["GET"])
@jwt_required()
def get_credentials():
    email = get_jwt_identity()
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if not user:
        session.close()
        return jsonify({"api_key": "", "ssid": "", "password": ""}), 200
    api_key = decrypt_api_key(user.api_key_encrypted) if user.api_key_encrypted else ""
    ssid = decrypt_api_key(user.wifi_ssid_encrypted) if user.wifi_ssid_encrypted else ""
    password = decrypt_api_key(user.wifi_password_encrypted) if user.wifi_password_encrypted else ""
    session.close()
    return jsonify({
        "api_key": api_key,
        "ssid": ssid,
        "password": password
    }), 200


# ========== Routers ==========

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not username or not password:
        return jsonify({"error": "Усі поля обов’язкові"}), 400

    if len(password) < 8:
        return jsonify({"error": "Пароль має містити щонайменше 8 символів"}), 400

    session = Session()
    if session.query(User).filter_by(email=email).first():
        session.close()
        return jsonify({"error": "Користувач з таким email вже існує"}), 400

    if session.query(User).filter_by(username=username).first():
        session.close()
        return jsonify({"error": "Ім’я користувача вже зайняте"}), 400

    new_user = User(
        email=email,
        username=username,
        password_hash=hash_password(password)
    )
    session.add(new_user)
    session.commit()
    session.close()

    return jsonify({"message": "Користувача зареєстровано успішно!"}), 201


@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Protection from brute-force
def login():
    data = request.get_json()
    login_input = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    session = Session()
    user = session.query(User).filter(
        (User.email == login_input) | (User.username == login_input)
    ).first()

    if not user or not check_password(password, user.password_hash):
        session.close()
        return jsonify({"error": "Невірний email/username або пароль"}), 401

    token = create_access_token(identity=user.email)
    session.close()
    return jsonify({"token": token})


@app.route("/ask", methods=["POST"])
@jwt_required()
def ask():
    email = get_jwt_identity()
    data = request.get_json()
    question = data.get("question", "").strip()
    
    # Get the key from the header
    openai_key = request.headers.get("X-OpenAI-Key", "").strip()
    if not openai_key:
        return jsonify({"error": "API ключ не вказано!"}), 401
    
    openai.api_key = openai_key

    if not question:
        return jsonify({"error": "Порожній запит"}), 400

    if profanity.contains_profanity(question):
        return jsonify({"error": "Запит містить заборонені слова."}), 400

    # ChatGPT API connetion
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти — доброзичливий помічник-іграшка для дітей, старайся уникати питань які можуть зашкодити дитині."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({"error": f"GPT помилка: {str(e)}"}), 500

    # Save history
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if user:
        msg = MessageHistory(question=question, user=user)
        session.add(msg)
        session.commit()
    session.close()

    # Generate MP3
    try:
        tts = gTTS(answer, lang="uk")
        filename = f"response_{uuid.uuid4()}.mp3"
        filepath = os.path.join("responses", filename)
        os.makedirs("responses", exist_ok=True)
        tts.save(filepath)
        return send_file(filepath, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": f"TTS помилка: {str(e)}"}), 500

@app.route("/history", methods=["GET"])
@jwt_required()
def history():
    email = get_jwt_identity()
    session = Session()
    user = session.query(User).filter_by(email=email).first()

    if not user:
        session.close()
        return jsonify({"error": "Користувача не знайдено"}), 404

    history_data = [
        {
            "question": h.question,
            "timestamp": h.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for h in reversed(user.history)
    ]

    session.close()
    return jsonify({"history": history_data})

@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"error": "Недійсний або відсутній токен доступу"}), 401

# ========== Start ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
