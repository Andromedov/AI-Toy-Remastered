from dotenv import load_dotenv
import flet as ft
import requests
import os
import json
from pathlib import Path
from teddy_view import TeddyAI
from login_view import LoginView

# Завантаження змінних середовища
load_dotenv()
CONFIG_FILE = Path("./.config.json")
FLASK_SERVER_URL = os.getenv("SERVER_URL")

# TODO: Fix main.py
def main(page: ft.Page):
    def start_teddy():
        with open(CONFIG_FILE, "r") as f:
            token = json.load(f).get("jwt_token", "")
        TeddyAI(page, jwt_token=token)

    # Якщо токен є — одразу запускаємо Teddy
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            if "jwt_token" in json.load(f):
                return start_teddy()

    # Інакше — відкриваємо форму логіну
    LoginView(page, on_login_success=start_teddy, server_url=FLASK_SERVER_URL)