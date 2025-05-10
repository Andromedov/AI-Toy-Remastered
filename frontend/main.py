from dotenv import load_dotenv
import flet as ft
import requests
import os
import json
import tempfile

load_dotenv()
CONFIG_FILE = ".config.json"
FLASK_SERVER_URL = os.getenv("SERVER_URL")

def load_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("api_key", "")
    return ""

def save_api_key(api_key):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key}, f)

def main(page: ft.Page):
    page.title = "TeddyAI - Android"
    page.window_width = 500
    page.window_height = 300
    page.scroll = ft.ScrollMode.AUTO

    api_key_field = ft.TextField(label="OpenAI API Key", password=True, value=load_api_key(), expand=True)
    question_field = ft.TextField(label="Питання до GPT", multiline=True, expand=True)
    status_text = ft.Text()

    def save_key(e):
        save_api_key(api_key_field.value)
        status_text.value = "🔐 Ключ збережено!"
        page.update()

    def send_question(e):
        question = question_field.value.strip()
        if not question:
            status_text.value = "❗ Введіть питання!"
            page.update()
            return

        api_key = api_key_field.value.strip()
        if not api_key:
            status_text.value = "❗ Спершу введіть API ключ!"
            page.update()
            return

        try:
            response = requests.post(
                FLASK_SERVER_URL,
                json={"question": question},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60
            )

            if response.status_code == 200:
                # Тимчасовий MP3-файл
                tmp_path = os.path.join(tempfile.gettempdir(), "response.mp3")
                with open(tmp_path, "wb") as f:
                    f.write(response.content)

                status_text.value = "✅ Відповідь збережено (відкрий вручну в програвачі)"
            else:
                status_text.value = f"❌ Помилка: {response.status_code} {response.text}"
        except Exception as ex:
            status_text.value = f"❌ Помилка: {ex}"
        page.update()

    page.add(
        ft.Column([
            ft.Row([api_key_field, ft.ElevatedButton("💾", on_click=save_key)]),
            question_field,
            ft.ElevatedButton("📤 Надіслати запит", on_click=send_question),
            status_text
        ])
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
