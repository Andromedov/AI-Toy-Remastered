from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, MessageHistory
from utils import hash_password, check_password
from gtts import gTTS
from better_profanity import profanity
from dotenv import load_dotenv
import openai
import os
import uuid

# ========== Settings ==========
load_dotenv("../.env")

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Connection to SQLite
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

profanity.load_censor_words_from_file("../.wordlist/banword_list.txt")

# ========== Routers ==========

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not email or not username or not password:
        return jsonify({"error": "Усі поля обов’язкові"}), 400

    session = Session()
    if session.query(User).filter_by(email=email).first():
        session.close()
        return jsonify({"error": "Користувач з таким email вже існує"}), 400

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
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    session = Session()
    user = session.query(User).filter_by(email=email).first()

    if not user or not check_password(password, user.password_hash):
        session.close()
        return jsonify({"error": "Невірний email або пароль"}), 401

    token = create_access_token(identity=email)
    session.close()
    return jsonify({"token": token})


@app.route("/ask", methods=["POST"])
@jwt_required()
def ask():
    email = get_jwt_identity()
    data = request.get_json()
    question = data.get("question", "").strip()
    
    # Get the key from the header
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not api_key:
        return jsonify({"error": "API ключ не вказано!"}), 401
    
    openai.api_key = api_key

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


# ========== Start ==========
if __name__ == "__main__":
    app.run(debug=True)
