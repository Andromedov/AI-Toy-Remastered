import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("API_URL", "http://localhost:5000/ask")

question = "Хто такий тигр?"

response = requests.post(
    BASE_URL,
    json={"question": question}
)

if response.status_code == 200:
    with open("answer.mp3", "wb") as f:
        f.write(response.content)
    print("✅ Файл answer.mp3 збережено.")
else:
    print(f"❌ Помилка: {response.status_code}")
    print(response.text)
