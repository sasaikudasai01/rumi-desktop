import flet as ft
import config as cfg
from start import startview
from edit_page import edit_data
from player import music_player
from settings_page import settings

def main(page: ft.Page):
    page.title = "rumi-desktop"
    page.window.icon = cfg.resource_path("color/icon_sq.ico")
    page.window.maximized = True

    # управление на клавиатуре
    def make_fullscreen(e: ft.KeyboardEvent):
        # полноэкранный режим
        if e.key == "F11":
            page.window.full_screen = not page.window.full_screen
            page.update()

    page.on_keyboard_event = make_fullscreen

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(startview(page))
        elif page.route == "/edit":
            page.views.append(edit_data(page))
        elif page.route == "/music_player":
            page.views.append(music_player(page))
        elif page.route == "/settings":
            page.views.append(settings(page))

        #page.views.append(music_player(page))
        page.update()

    def view_pop(e):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)