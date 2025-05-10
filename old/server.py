from flask import Flask, request, send_file, jsonify
from gtts import gTTS
from better_profanity import profanity
from dotenv import load_dotenv
import openai
import os
import uuid

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
profanity.load_censor_words_from_file("custom_wordlist/banword_list.txt")

@app.route("/ask", methods=["POST"])
def handle_question():
    data = request.json
    question = data.get("question", "").strip()

    if profanity.contains_profanity(question):
        return jsonify({"error": "Запит містить заборонені слова."}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти — добрий іграшковий помічник, який спілкується з дітьми. Не говори про насильство, погані теми, або грубість."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({"error": f"GPT помилка: {str(e)}"}), 500

    try:
        tts = gTTS(answer, lang="uk")
        filename = f"response_{uuid.uuid4()}.mp3"
        filepath = os.path.join("responses", filename)
        os.makedirs("responses", exist_ok=True)
        tts.save(filepath)
        return send_file(filepath, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": f"Помилка озвучення: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
