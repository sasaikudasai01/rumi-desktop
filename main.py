import flet as ft
from start import startview
from edit_page import edit_data

def main(page: ft.Page):
    page.title = "rumi-desktop"

    def route_change(e):
        page.views.clear()
        if page.route == "/":
            page.views.append(startview(page))
        elif page.route == "/edit":
            page.views.append(edit_data(page))
        page.update()

    def view_pop(e):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)
