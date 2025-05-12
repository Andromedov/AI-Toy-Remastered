from dotenv import load_dotenv
import flet as ft
import os
import json
from pathlib import Path
from teddy_view import TeddyAI
from login_view import LoginView

# Завантаження .env
load_dotenv("../.env")
CONFIG_FILE = Path("./.config.json")
FLASK_SERVER_URL = os.getenv("SERVER_URL")

def main(page: ft.Page):
    page.title = "TeddyAI"
    page.window_width = 500
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.SYSTEM

    # Callback after login
    def start_teddy():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                token = config.get("jwt_token", "")
                if token:
                    page.clean()  # Clean page before start
                    TeddyAI(page, jwt_token=token)
        except Exception as e:
            print(f"❌ Помилка при запуску TeddyAI: {e}")
            page.add(ft.Text("Не вдалося запустити TeddyAI", color=ft.Colors.RED))

    # If token exist - run Teddy
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                if "jwt_token" in data and data["jwt_token"].strip():
                    return start_teddy()
        except Exception as e:
            print(f"⚠️ Не вдалося прочитати конфіг: {e}")

    # Else - show login screen
    page.clean()
    LoginView(page, on_login_success=start_teddy, server_url=FLASK_SERVER_URL)

# Start Flet program
if __name__ == "__main__":
    ft.app(target=main)
