import flet as ft
from flask import Flask, request, send_file, jsonify

def main(page: ft.Page):
    def button_clicked(e):
        t.value = f"API Key is:  '{tb1.value}'."
        page.update()

    t = ft.Text()
    tb1 = ft.TextField(label="API Key", hint_text="Please enter OpenAI API Key here")
    b = ft.ElevatedButton(text="Submit", on_click=button_clicked)
    page.add(tb1, b, t)


ft.app(main)