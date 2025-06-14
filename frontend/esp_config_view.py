
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

class ESPSetupView:
    def __init__(self, page: ft.Page, on_back=None):
        self.page = page
        self.on_back = on_back

        self.esp_ip = ft.TextField(label="IP ESP32", value="192.168.4.1", expand=True)
        self.ssid_field = ft.TextField(label="WiFi SSID", expand=True)
        self.pass_field = ft.TextField(label="WiFi пароль", password=True, can_reveal_password=True, expand=True)
        self.email_field = ft.TextField(label="Email або Username", expand=True)
        self.user_pass_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True, expand=True)

        self.status_text = ft.Text("")
        self.submit_btn = ft.ElevatedButton("Відправити", icon=ft.Icons.SEND, on_click=self.send_config)
        self.back_btn = ft.TextButton("← Назад", on_click=self.back_to_teddy)

        self.page.clean()
        self.load_saved_wifi()

        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Налаштування ESP32 через точку доступу", size=22, weight=ft.FontWeight.BOLD),
                    self.esp_ip,
                    self.ssid_field,
                    self.pass_field,
                    self.email_field,
                    self.user_pass_field,
                    self.submit_btn,
                    self.status_text,
                    self.back_btn
                ],
                expand=True,
                spacing=10),
                padding=20
            )
        )

    def load_saved_wifi(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                encrypted_ssid = data.get("wifi_ssid", "")
                encrypted_pass = data.get("wifi_password", "")
                fernet = get_fernet()
                if encrypted_ssid:
                    self.ssid_field.value = fernet.decrypt(encrypted_ssid.encode()).decode()
                if encrypted_pass:
                    self.pass_field.value = fernet.decrypt(encrypted_pass.encode()).decode()
        except Exception as e:
            print(f"Не вдалося завантажити Wi-Fi: {e}")

    def send_config(self, _):
        ip = self.esp_ip.value.strip()
        ssid_value = self.ssid_field.value.strip()
        pwd_value = self.pass_field.value.strip()
        email = self.email_field.value.strip()
        user_pwd = self.user_pass_field.value.strip()

        if not ssid_value or not email or not user_pwd:
            self.status_text.value = "❗ Заповніть усі поля"
            self.page.update()
            return

        try:
            r = requests.post(f"http://{ip}/setup", data={
                "ssid": ssid_value,
                "pass": pwd_value,
                "email": email,
                "pwd": user_pwd
            }, timeout=10)

            if r.status_code == 200:
                self.status_text.value = "✅ Дані успішно передані! ESP має перезапуститись."

                fernet = get_fernet()
                data = {
                    "wifi_ssid": fernet.encrypt(ssid_value.encode()).decode(),
                    "wifi_password": fernet.encrypt(pwd_value.encode()).decode()
                }

                try:
                    if CONFIG_FILE.exists():
                        with open(CONFIG_FILE, "r") as f:
                            old = json.load(f)
                    else:
                        old = {}

                    old.update(data)
                    with open(CONFIG_FILE, "w") as f:
                        json.dump(old, f)
                except Exception as e:
                    print(f"Не вдалося зберегти Wi-Fi: {e}")
            else:
                self.status_text.value = f"❌ Помилка: {r.status_code}"
        except Exception as ex:
            self.status_text.value = f"❌ Виняток: {ex}"

        self.page.update()

    def back_to_teddy(self, e):
        if self.on_back:
            self.page.clean()
            self.on_back()
