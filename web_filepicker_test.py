#!/usr/bin/env python3
import flet as ft

def main(page: ft.Page):
    page.title = "Web FilePicker Test"
    
    def on_result(e):
        print(f"Result: {e}")
        if e.files:
            for f in e.files:
                print(f"Selected: {f.path}")
    
    # Создаем FilePicker
    file_picker = ft.FilePicker(on_result=on_result)
    page.overlay.append(file_picker)
    page.update()
    
    def pick_files(e):
        print("Button clicked!")
        file_picker.pick_files(allow_multiple=True)
    
    page.add(
        ft.Text("Web FilePicker Test", size=20),
        ft.ElevatedButton("Pick Files", on_click=pick_files)
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
