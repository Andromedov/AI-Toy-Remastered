import flet as ft
import requests
import os
import json
import tempfile
import asyncio
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from cryptography.fernet import Fernet

timestamp = datetime.now().strftime("%H:%M:%S")

load_dotenv(find_dotenv())
CONFIG_FILE = Path(".config.json")
FERNET_FILE = Path(".fernet.key")
FLASK_SERVER_URL = os.getenv("SERVER_URL")

def get_fernet():
    if FERNET_FILE.exists():
        key = FERNET_FILE.read_text().strip()
    else:
        key = Fernet.generate_key().decode()
        FERNET_FILE.write_text(key)
    return Fernet(key.encode())

class TeddyAI:
    def __init__(self, page: ft.Page, jwt_token: str):
        self.page = page
        self.jwt_token = jwt_token
        self.setup_page()
        self.load_components()
        
    def setup_page(self):
        self.page.title = "TeddyAI"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Adaptive customization depending on the platform
        if self.page.platform == "android":
            self.page.window.width = self.page.width
            self.page.window.height = self.page.height
        else:
            self.page.window.width = 500
            self.page.window.height = 650
        
    def load_components(self):
        # Loading a saved API key
        saved_key = self.load_api_key()
        self.history_list = ft.ListView(expand=True, spacing=10, height=200)

        # Creation of logout button
        self.logout_button = ft.TextButton(
            text="Вийти",
            icon=ft.Icons.LOGOUT,
            on_click=self.logout,
            style=ft.ButtonStyle(padding=ft.Padding(10, 4, 10, 4))
        )

        self.history_panel = ft.Container(
            content=ft.Column([
                ft.Text("Історія", weight=ft.FontWeight.BOLD),
                self.history_list
            ]),
            padding=ft.Padding(10, 10, 10, 10),
            visible=False
        )

        # Creation of UI elements
        self.api_key_field = ft.TextField(
            label="OpenAI API Key",
            password=True,
            can_reveal_password=True,
            value=saved_key,
            expand=True,
            border=ft.InputBorder.UNDERLINE,
            prefix_icon=ft.Icons.KEY
        )
        
        self.question_field = ft.TextField(
            label="Питання до GPT",
            multiline=True,
            min_lines=3,
            max_lines=5,
            expand=True,
            border=ft.InputBorder.UNDERLINE,
            hint_text="Напишіть своє питання тут...",
            prefix_icon=ft.Icons.QUESTION_ANSWER
        )
        
        self.status_text = ft.Text(
            size=14,
            color=ft.Colors.BLUE_GREY_400
        )
        
        self.progress_bar = ft.ProgressBar(visible=False)
        self.audio_file_path = None
        
        self.audio_controls = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Відтворити у плеєрі",
                    icon=ft.Icons.PLAY_ARROW, 
                    on_click=self.play_audio,
                    disabled=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False
        )
        
        # Buttons
        self.save_key_btn = ft.IconButton(
            icon=ft.Icons.SAVE,
            tooltip="Зберегти ключ",
            on_click=self.save_key,
        )
        
        self.send_question_btn = ft.ElevatedButton(
            "Надіслати запит",
            icon=ft.Icons.SEND,
            on_click=self.send_question,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.BLUE_600
            )
        )
        
        # Component structure
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("TeddyAI", size=30, weight=ft.FontWeight.BOLD),
                        self.logout_button
                    ]),
                    ft.Text("Голосовий асистент на базі GPT", size=16, color=ft.Colors.BLUE_GREY_400),
                    ft.Divider(),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Налаштування API", weight=ft.FontWeight.BOLD),
                            ft.Row([
                                self.api_key_field,
                                self.save_key_btn
                            ]),
                        ]),
                        padding=ft.Padding(10, 10, 10, 10)
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Ваше питання", weight=ft.FontWeight.BOLD),
                            self.question_field,
                            ft.Container(height=10),
                            self.send_question_btn,
                            self.progress_bar,
                        ]),
                        padding=ft.Padding(0, 0, 0, 10)
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Статус", weight=ft.FontWeight.BOLD),
                            self.status_text,
                            self.audio_controls,
                        ]),
                        padding=ft.Padding(0, 0, 0, 10)
                    ),

                    ft.Container(
                        content=ft.Column([
                            ft.Text("Історія", weight=ft.FontWeight.BOLD),
                            self.history_list
                        ]),
                        padding=ft.Padding(0, 0, 0, 10)
                    ),
                ]),
                padding=ft.Padding(10, 10, 10, 10),
                border_radius=10,
            ),
            # Removed link to audio player
        )
        
    def load_api_key(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    encrypted_key = json.load(f).get("api_key", "")
                if encrypted_key:
                    fernet = get_fernet()
                    return fernet.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            print(f"Помилка читання ключа: {e}")
        return ""
    
    async def save_api_key(self, api_key):
        try:
            fernet = get_fernet()
            encrypted_key = fernet.encrypt(api_key.encode()).decode()

            # Локально
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            data["api_key"] = encrypted_key
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)

            # На сервер
            response = requests.post(
                f"{FLASK_SERVER_URL}/save_api_key",
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                json={"api_key": api_key},
                timeout=10
            )
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                await self.auto_logout_and_login()
                self.jwt_token = ""
                return False
            else:
                print("❌ Помилка при надсиланні ключа:", response.text)
                return False
        except Exception as e:
            print("❌ Помилка збереження ключа:", e)
            return False

    def save_key(self, e):
        asyncio.run(self._save_key_async(e))

    async def _save_key_async(self, _):
        if not self.api_key_field.value:
            self.show_snackbar("Введіть API ключ!")
            return
            
        if await self.save_api_key(self.api_key_field.value):
            self.show_snackbar("🔐 Ключ успішно збережено!")
        else:
            self.show_snackbar("❌ Помилка збереження ключа")
    
    async def send_question(self, e):
        question = self.question_field.value.strip()
        api_key = self.api_key_field.value.strip()
        
        # Verify the entered data
        if not question:
            self.show_snackbar("❗ Введіть питання!")
            return
            
        if not api_key:
            self.show_snackbar("❗ Спершу введіть API ключ!")
            return
        
        self.history_list.controls.insert(0, ft.Row([
            ft.Icon(ft.Icons.QUESTION_ANSWER, size=18),
            ft.Text(question, size=14, expand=True),
            ft.Text(timestamp, size=12, color=ft.Colors.BLUE_GREY),
            ft.IconButton(icon=ft.Icons.PLAY_ARROW, on_click=lambda e, p=self.audio_file_path: self.play_audio_from_path(p))
        ]))
        self.history_panel.visible = True
        self.page.update()
        # Show the download progress
        self.progress_bar.visible = True
        self.send_question_btn.disabled = True
        self.status_text.value = "Відправлення запиту..."
        self.page.update()
        
        try:
            # Asynchronous query execution
            response_result, error_message = await asyncio.to_thread(self._make_request, question, api_key)

            if response_result == True:
                self.status_text.value = "✅ Відповідь отримана"
                self.audio_controls.visible = True
                self.enable_audio_controls(True)
            elif response_result == "unauthorized":
                await self.auto_logout_and_login()
            else:
                self.status_text.value = "❌ Не вдалося отримати відповідь"
                if error_message:
                    self.show_snackbar(error_message)
                
        except Exception as ex:
            self.status_text.value = f"❌ Помилка: {ex}"
            
        finally:
            # Remove progress
            self.progress_bar.visible = False
            self.send_question_btn.disabled = False
            self.page.update()

    def play_audio_from_path(self, path):
        try:
            if platform.system() == "Windows":
               os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as ex:
            self.show_snackbar(f"Не вдалося відтворити: {ex}")

    def _make_request(self, question, api_key):
        try:
            # Send a POST request to the Flask server
            response = requests.post(
               f"{FLASK_SERVER_URL}/ask",
               json={"question": question},
               headers={
                   "Authorization": f"Bearer {self.jwt_token}",
                   "X-OpenAI-Key": api_key
                },
               timeout=120  # 2 minutes
            )

            if response.status_code == 200:
                # Successful answer - save audio to a temporary file
                tmp_dir = Path(tempfile.gettempdir())
                tmp_path = tmp_dir / "teddyai_response.mp3"

                with open(tmp_path, "wb") as f:
                    f.write(response.content)

                # Save the path for future use
                self.audio_file_path = str(tmp_path)

                return True, None  # Return “success” and None as no error
            
            if response.status_code == 401:
                return "unauthorized", "Сесія завершена або токен недійсний"

            else:
                # Generate the error message
                error_msg = f"Сервер повернув помилку: {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f" - {error_details.get('error', '')}"
                except (ValueError, KeyError):
                    pass

                return False, error_msg

        except requests.RequestException as e:
            # Network error - for example, the server is unavailable
            return False, f"Помилка підключення: {e}"

        except Exception as e:
            # Other, unexpected errors
            return False, f"Непередбачена помилка: {e}"
    
    # TODO: Fix Snackbar if not work 
    def show_snackbar(self, message):
        self.page.snackbar = ft.SnackBar(
            content=ft.Text(message),
            action="OK",
            duration=3000,
        )
        self.page.snackbar.open = True
        self.page.update()
    
    def enable_audio_controls(self, enabled=True):
        for btn in self.audio_controls.controls:
            btn.disabled = not enabled
    
    def play_audio(self, _):
        if self.audio_file_path:
            try:
                # Open a file in the system player
                if platform.system() == "Windows": # Windows
                    os.startfile(self.audio_file_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.call(["open", self.audio_file_path])
                else:  # Linux & Android
                    subprocess.call(["xdg-open", self.audio_file_path])
            except Exception as ex: # Error ¯\_(ツ)_/¯
                self.show_snackbar(f"Помилка відтворення: {ex}")
        self.page.update()

    # TODO: Fix pause and stop audio players
    def pause_audio(self, _):
        self.show_snackbar("Керуйте відтворенням у системному плеєрі")
        self.page.update()
    
    def stop_audio(self, _):
        self.show_snackbar("Керуйте відтворенням у системному плеєрі")
        self.page.update()

    def show_login_view(self):
        from login_view import LoginView
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        def on_login_success():
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    token = config.get("jwt_token", "")
                    if token:
                        self.page.clean()
                        TeddyAI(self.page, jwt_token=token)
            except Exception as ex:
                print("❌ Не вдалося прочитати токен після логіну:", ex)

        LoginView(self.page, on_login_success=on_login_success, server_url=FLASK_SERVER_URL)


    def logout(self, e):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                data.pop("jwt_token", None)  # Remove token
                with open(CONFIG_FILE, "w") as f:
                    json.dump(data, f)
        except Exception as ex:
            print(f"Помилка при видаленні токена: {ex}")

        self.show_login_view()

    async def auto_logout_and_login(self):
        try:
            # Видаляємо токен
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                data.pop("jwt_token", None)
                with open(CONFIG_FILE, "w") as f:
                    json.dump(data, f)

            # Повертаємось до екрана входу
            await asyncio.sleep(1)
            self.show_login_view()
        except Exception as ex:
            print(f"Помилка при auto-logout: {ex}")


def main(page: ft.Page):
    TeddyAI(page)