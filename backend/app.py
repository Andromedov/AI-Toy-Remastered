from flask import Flask, request, jsonify, send_file
from gtts import gTTS
from better_profanity import profanity
from dotenv import load_dotenv
import openai
import os
import json
import uuid

load_dotenv()

def load_api_key_from_config():
    try:
        with open("../frontend/.config.json", "r") as f:
            config_data = json.load(f)
            return config_data.get("api_key", "")
    except Exception as e:
        print(f"Помилка при читанні .config.json: {e}")
        return ""
    
api_key = load_api_key_from_config()

if not api_key:
    raise ValueError("API ключ не знайдений! Перевірте .config.json або .env")

openai.api_key = api_key

app = Flask(__name__)
profanity.load_censor_words_from_file("../.wordlist/banword_list.txt")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Порожній запит"}), 400

    if profanity.contains_profanity(question):
        return jsonify({"error": "Запит містить заборонені слова."}), 400

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
    
    print(f"GPT відповів: {answer}")

    try:
        tts = gTTS(answer, lang="uk")
        filename = f"response_{uuid.uuid4()}.mp3"
        filepath = os.path.join("responses", filename)
        os.makedirs("responses", exist_ok=True)
        tts.save(filepath)
        print(f"MP3 збережено в: {filepath}, розмір: {os.path.getsize(filepath)} байт")
        return send_file(filepath, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": f"TTS помилка: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
