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
from dotenv import load_dotenv

timestamp = datetime.now().strftime("%H:%M:%S")

load_dotenv("../.env")
CONFIG_FILE = Path(".config.json")
FLASK_SERVER_URL = os.getenv("SERVER_URL")

class TeddyAI:
    def __init__(self, page: ft.Page, jwt_token: str):
        self.page = page
        self.jwt_token = jwt_token
        self.setup_page()
        self.load_components()
        
    def setup_page(self):
        """Налаштування сторінки"""
        self.page.title = "TeddyAI"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Adaptive customization depending on the platform
        if self.page.platform == "android":
            self.page.window_width = self.page.width
            self.page.window_height = self.page.height
        else:
            self.page.window_width = 500
            self.page.window_height = 650
        
    def load_components(self):
        """Завантаження всіх компонентів інтерфейсу"""
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
        
        self.logout_button = ft.TextButton(
            text="Вийти",
            icon=ft.Icons.LOGOUT,
            on_click=self.logout,
            style=ft.ButtonStyle(padding=ft.Padding(10, 4, 10, 4))
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
        """Завантаження API ключа з конфігураційного файлу"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f).get("api_key", "")
        except Exception as e:
            print(f"Помилка читання ключа: {e}")
        return ""
    
    def save_api_key(self, api_key):
        """Збереження API ключа в конфігураційний файл"""
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"api_key": api_key}, f)
            return True
        except Exception as e:
            print(f"Помилка збереження ключа: {e}")
            return False
    
    def save_key(self, e):
        """Обробник події збереження ключа"""
        if not self.api_key_field.value:
            self.show_snackbar("Введіть API ключ!")
            return
            
        if self.save_api_key(self.api_key_field.value):
            self.show_snackbar("🔐 Ключ успішно збережено!")
        else:
            self.show_snackbar("❌ Помилка збереження ключа")
    
    async def send_question(self, e):
        """Обробник події відправки питання"""
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
            response_success, error_message = await asyncio.to_thread(self._make_request, question, api_key)

            if response_success:
                self.status_text.value = "✅ Відповідь отримана"
                self.audio_controls.visible = True
                self.enable_audio_controls(True)
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
        """Виконання HTTP запиту до сервера та збереження аудіо"""
        try:
            # Send a POST request to the Flask server
            response = requests.post(
               FLASK_SERVER_URL,
               json={"question": question},
               headers={"Authorization": f"Bearer {self.jwt_token}"},
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
    
    def show_snackbar(self, message):
        """Показує спливаюче повідомлення"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            action="OK"
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def enable_audio_controls(self, enabled=True):
        """Вмикає/вимикає кнопки керування аудіо"""
        for btn in self.audio_controls.controls:
            btn.disabled = not enabled
    
    def play_audio(self, _):
        """Відтворення аудіо в системному плеєрі"""
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
    
    def pause_audio(self, _):
        """Пауза аудіо - системний плеєр керується окремо"""
        self.show_snackbar("Керуйте відтворенням у системному плеєрі")
        self.page.update()
    
    def stop_audio(self, _):
        """Зупинка аудіо - системний плеєр керується окремо"""
        self.show_snackbar("Керуйте відтворенням у системному плеєрі")
        self.page.update()

    def logout(self, e):
        """Вихід з облікового запису"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                data.pop("jwt_token", None)  # Remove token
                with open(CONFIG_FILE, "w") as f:
                    json.dump(data, f)
        except Exception as ex:
            print(f"Помилка при видаленні токена: {ex}")

    # Return to login page
        self.page.clean()
        from login_view import LoginView
        LoginView(
            self.page,
            on_login_success=lambda: TeddyAI(self.page, jwt_token=""),
            server_url=FLASK_SERVER_URL
        )


def main(page: ft.Page):
    """Головна функція, що ініціалізує застосунок"""
    TeddyAI(page)  # Create an instance without saving the reference