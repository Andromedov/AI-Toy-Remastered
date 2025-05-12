import flet as ft
import requests
import json
from pathlib import Path
from cryptography.fernet import Fernet

CONFIG_FILE = Path(".config.json")
FERNET_FILE = Path(".fernet.key")

def get_fernet():
    if FERNET_FILE.exists():
        key = FERNET_FILE.read_text().strip()
    else:
        key = Fernet.generate_key().decode()
        FERNET_FILE.write_text(key)
    return Fernet(key.encode())

class LoginView:
    def __init__(self, page: ft.Page, on_login_success, server_url: str):
        self.page = page
        self.on_login_success = on_login_success
        self.server_url = server_url

        self.email_field = ft.TextField()
        self.username_field = ft.TextField()
        self.password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)

        self.status_text = ft.Text("")
        self.is_login_mode = True

        self.action_button = ft.ElevatedButton(text="...", on_click=self.authenticate)
        self.switch_mode_button = ft.TextButton(on_click=self.toggle_mode)

        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("TeddyAI", size=30, weight=ft.FontWeight.BOLD),
                    self.email_field,
                    self.username_field,
                    self.password_field,
                    self.action_button,
                    self.switch_mode_button,
                    self.status_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0.0, 0.0),
                expand=True,
                padding=20
            )
        )


        self.update_fields()

    def update_fields(self):
        if self.is_login_mode:
            self.email_field.label = "Ім'я користувача або Email"
            self.username_field.visible = False
            self.action_button.text = "Увійти"
            self.switch_mode_button.text = "Ще не маєш акаунту? Зареєструйся"
        else:
            self.email_field.label = "Email"
            self.username_field.label = "Ім’я користувача"
            self.username_field.visible = True
            self.action_button.text = "Зареєструватись"
            self.switch_mode_button.text = "У тебе вже є акаунт? Увійди"
        self.page.update()

    def toggle_mode(self, e):
        self.is_login_mode = not self.is_login_mode
        self.update_fields()

    def authenticate(self, e):
        email = self.email_field.value.strip()
        password = self.password_field.value.strip()
        username = self.username_field.value.strip()

        if not email or not password or (not self.is_login_mode and not username):
            self.status_text.value = "❗ Заповніть усі поля"
            self.page.update()
            return

        try:
            if self.is_login_mode:
                r = requests.post(f"{self.server_url}/login", json={"email": email, "password": password})
            else:
                r = requests.post(f"{self.server_url}/register", json={
                    "email": email, "password": password, "username": username
                })
                if r.status_code == 201:
                    self.status_text.value = "✅ Реєстрація успішна. Тепер увійдіть."
                    self.is_login_mode = True
                    self.update_fields()
                    return

            if r.status_code == 200:
                token = r.json()["token"]

                key = ""
                try:
                    key_resp = requests.get(
                        f"{self.server_url}/api-key",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if key_resp.status_code == 200:
                        key = key_resp.json().get("api_key", "")
                except Exception as ex:
                    print("⚠️ Не вдалося отримати ключ:", ex)
                    
                self.save_config(email=email, jwt=token, api_key=key)
                self.status_text.value = "✅ Успішний вхід!"
                self.page.clean()
                self.on_login_success()
            else:
                self.status_text.value = f"❌ Помилка: {r.json().get('error', 'Невідома')}"
        except Exception as ex:
            self.status_text.value = f"❌ Виняток: {ex}"

        self.page.update()

    def save_config(self, email, jwt, api_key=None):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = {}

            data["email"] = email
            data["jwt_token"] = jwt
            if api_key:
                fernet = get_fernet()
                data["api_key"] = fernet.encrypt(api_key.encode()).decode()

            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Не вдалося зберегти токен: {e}")
