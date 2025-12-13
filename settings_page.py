import flet as ft
import config as cfg
import json



def settings(page: ft.Page):
    # окно выбора изображения
    def pick_file(e):
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])  # только один файл

    # сохранение пути к изображению
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            cfg.wallpaper = e.files[0].path
            background_image.src = e.files[0].path

            # параметры которые нужно сохранить в user_setting.json
            cfg.user_settings['wallpaper_path'] = e.files[0].path

            # сохранение в user_setting.json
            with open("user_setting.json", "w", encoding="UTF-8") as f:
                json.dump(cfg.user_settings, f, ensure_ascii=False, indent=2)

            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # кнопка замены обоев
    change_wallpaper_button = ft.Container(
        content=ft.Image(
            src=cfg.resource_path("icons/settings_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            color=cfg.not_main_color_hex,
            width=55,
            height=55,
        ),
        width=55,
        height=55,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda _: pick_file(_),
    )



    def get_color_hex_submit(_, main_not_main):
        # main_not_main это основной или неосновной цвет
        if main_not_main == "not_main":

            if cfg.is_hex_color(get_not_main_color_hex_input.value):
                cfg.user_settings["not_main_color_hex"] = get_not_main_color_hex_input.value

            # если введено default, то применить стандартные цвета
            elif get_not_main_color_hex_input.value.lower() == "default":
                cfg.user_settings.pop("not_main_color_hex")
                cfg.main_color_hex = "#EBD0E1"

            else: cfg.user_settings["not_main_color_hex"] = cfg.not_main_color_hex

        else:
            if cfg.is_hex_color(get_main_color_hex_input.value):
                cfg.user_settings["main_color_hex"] = get_main_color_hex_input.value

            elif get_main_color_hex_input.value.lower() == "default":
                cfg.user_settings.pop("main_color_hex")
                cfg.main_color_hex = "#FE3C79"

            else: cfg.user_settings["main_color_hex"] = cfg.main_color_hex

        # сохранение в user_setting.json
        with open("user_setting.json", "w", encoding="UTF-8") as f:
            json.dump(cfg.user_settings, f, ensure_ascii=False, indent=2)

        page.update()

    # текст для замены цвета
    get_not_main_color_hex_input = ft.TextField(
        hint_text="not_main_color_hex",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_size=25,
        border_color="transparent",
        border_radius=15,
        on_submit=lambda _, main_or_not="not_main": get_color_hex_submit(_, main_or_not),
    )

    # текст для замены цвета
    get_main_color_hex_input = ft.TextField(
        hint_text="main_color_hex",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.main_color_hex),
        text_size=25,
        border_color="transparent",
        border_radius=15,
        on_submit=lambda _, main_or_not="main": get_color_hex_submit(_, main_or_not)
    )



    def back_to_download_page(_):
        page.go("/")

    # кнопка "вернуться к странице скачивания"
    to_download_page_button = ft.Container(
        content=ft.Image(
            src=cfg.resource_path("icons/home_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            color=cfg.not_main_color_hex,
            width=55,
            height=55,
        ),
        width=55,
        height=55,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e: back_to_download_page(e),
    )



    main_page = ft.Row(
        controls=[to_download_page_button, change_wallpaper_button, get_main_color_hex_input, get_not_main_color_hex_input],
    )

    background_image = ft.DecorationImage(
        src=cfg.wallpaper,
        fit=ft.ImageFit.COVER,
    )
    background = ft.BoxDecoration(
        image=background_image,
    )



    # управление на клавиатуре
    def make_fullscreen(e: ft.KeyboardEvent):
        # полноэкранный режим
        if e.key == "F11":
            page.window.full_screen = not page.window.full_screen
            page.update()

    page.on_keyboard_event = make_fullscreen



    return ft.View("/settings", controls=[main_page], bgcolor=ft.Colors.TRANSPARENT, decoration=background)