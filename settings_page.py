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
            with open(cfg.base_dir_files("user_setting.json"), "w", encoding="UTF-8") as f:
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



    # текст для замены цвета
    get_not_main_color_hex_input = ft.TextField(
        hint_text="not_main_color_hex",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_size=25,
        border_color="transparent",
        border_radius=15,
    )

    # текст для замены цвета
    get_main_color_hex_input = ft.TextField(
        hint_text="main_color_hex",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.main_color_hex),
        text_size=25,
        border_color="transparent",
        border_radius=15,
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



    # данные для spotify web api
    client_id_input = ft.TextField(
        hint_text="enter CLIENT_ID",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
        text_size=25,
        border_color="transparent",
        border_radius=15,
    )

    client_secret_input = ft.TextField(
        hint_text="enter CLIENT_SECRET",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
        text_size=25,
        border_color="transparent",
        border_radius=15,
    )

    if cfg.CLIENT_ID:
        client_id_input.hint_text = f'CLIENT_ID: {cfg.CLIENT_ID[:5]}***'

    if cfg.CLIENT_SECRET:
        client_secret_input.hint_text = f'CLIENT_SECRET: {cfg.CLIENT_SECRET[:5]}***'



    def apply_settings(_):
        if client_id_input.value or client_secret_input.value:
            with open(cfg.base_dir_files(".env"), "w", encoding="UTF-8") as env:
                env.write(f'SPOTIFY_CLIENT_ID={client_id_input.value}\nSPOTIFY_CLIENT_SECRET={client_secret_input.value}')

                cfg.CLIENT_ID = client_id_input.value
                cfg.CLIENT_SECRET = client_secret_input.value



        # colors apply ####################################
        main_color = get_main_color_hex_input.value.strip()
        not_main_color = get_not_main_color_hex_input.value.strip()

        if not main_color.startswith("#"):
            main_color = f'#{main_color}'

        if not not_main_color.startswith("#"):
            not_main_color = f'#{not_main_color}'

        if cfg.is_hex_color(main_color):
            cfg.user_settings["main_color_hex"] = main_color

        if cfg.is_hex_color(not_main_color):
            cfg.user_settings["not_main_color_hex"] = not_main_color



        # вернуть дефолтные цвета если введено default
        if main_color.lower() == "#default":
            cfg.user_settings.pop("main_color_hex")
            cfg.main_color_hex = "#FE3C79"

        if not_main_color.lower() == "#default":
            cfg.user_settings.pop("not_main_color_hex")
            cfg.not_main_color_hex = "#EBD0E1"



        with open(cfg.base_dir_files("user_setting.json"), "w", encoding="UTF-8") as f:
            json.dump(cfg.user_settings, f, ensure_ascii=False, indent=2)

    apply_button = ft.Stack(
        controls=[
            # visible button
            ft.FilledButton(
                ' ',
                bgcolor=cfg.main_color_hex,
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=250,
                height=45,
            ),

            # text on button
            ft.Container(
                content=ft.Text(
                    "Apply",
                    style=ft.TextStyle(
                        color=cfg.not_main_color_hex,
                        font_family="Gabarito",
                        size=30,
                        weight=ft.FontWeight.BOLD
                    ),
                ),
                alignment=ft.alignment.center,
                width=250,
                height=45,
            ),

            # actual transparent button
            ft.FilledButton(
                ' ',
                bgcolor=ft.Colors.TRANSPARENT,
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=250,
                height=45,
                on_click=apply_settings,
            ),
        ],
    )



    main_page = ft.Column(
        controls=[
            ft.Row(
                controls=[to_download_page_button, change_wallpaper_button,
                          get_main_color_hex_input, get_not_main_color_hex_input],
            ),
            ft.Row(
                controls=[client_id_input, client_secret_input, apply_button],
            )
        ]
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