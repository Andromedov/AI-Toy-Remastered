import flet as ft
import requests
import json
from pathlib import Path
from flet_webview import WebView

CONFIG_FILE = Path(".config.json")

class LoginView:
    def __init__(self, page: ft.Page, on_login_success, server_url: str):
        self.page = page
        self.on_login_success = on_login_success
        self.server_url = server_url

        self.email_field = ft.TextField(label="Email", keyboard_type="email")
        self.password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
        self.username_field = ft.TextField(label="Ім’я користувача (реєстрація)")

        self.status_text = ft.Text("")
        self.is_login_mode = True

        self.action_button = ft.ElevatedButton("Увійти", on_click=self.authenticate)
        self.switch_mode_button = ft.TextButton("Ще не маєш акаунту? Зареєструйся", on_click=self.toggle_mode)

        self.captcha_token = ""

        captcha_path = Path("./static/captcha.html").resolve().as_uri()
        self.captcha_view = WebView(
            url=captcha_path,
            height=300,
            width=400,
            visible=False
        )

        self.captcha_btn = ft.ElevatedButton(
            text="Пройти CAPTCHA",
            icon=ft.Icons.SECURITY,
            on_click=self.show_captcha
        )

        self.refresh_token_btn = ft.ElevatedButton(
            text="🔄 Отримати токен",
            on_click=self.read_captcha_token
        )

        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("TeddyAI", size=30, weight=ft.FontWeight.BOLD),
                    self.email_field,
                    self.password_field,
                    self.username_field,
                    ft.Row([
                        self.captcha_btn,
                        self.refresh_token_btn
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    self.captcha_view,
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
        self.username_field.visible = not self.is_login_mode
        self.action_button.text = "Увійти" if self.is_login_mode else "Зареєструватись"
        self.switch_mode_button.text = "Ще не маєш акаунту? Зареєструйся" if self.is_login_mode else "У тебе вже є акаунт? Увійди"
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
                r = requests.post(f"{self.server_url}/login", json={
                    "email": email, 
                    "password": password,
                    "captcha_token": self.captcha_token
                })
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
                self.save_config(email=email, jwt=token)
                self.status_text.value = "✅ Успішний вхід!"
                self.page.clean()
                self.on_login_success()
            else:
                self.status_text.value = f"❌ Помилка: {r.json().get('error', 'Невідома')}"
        except Exception as ex:
            self.status_text.value = f"❌ Виняток: {ex}"

        self.page.update()

    def show_snackbar(self, message):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK"
        )
        self.page.snack_bar.open = True
        self.page.update()


    def save_config(self, email, jwt):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = {}

            data["email"] = email
            data["jwt_token"] = jwt

            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Не вдалося зберегти токен: {e}")
    
    def show_captcha(self, e):
        self.captcha_view.visible = True
        self.page.update()

    def read_captcha_token(self, e):
        import pyperclip
        try:
            token = pyperclip.paste()
            if token.startswith("03"):
                self.captcha_token = token
                self.show_snackbar("✅ Токен зчитано!")
            else:
                self.show_snackbar("❌ Токен не знайдено. Скопіюйте його вручну.")
        except Exception as ex:
            self.show_snackbar(f"⚠️ Помилка зчитування токена: {ex}")

