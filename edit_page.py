import flet as ft
import time
import config
from mutagen.id3 import ID3, APIC, TIT2, TPE1, ID3NoHeaderError, TALB # изменение метаданных трека

def edit_data(page: ft.Page):
    # окно выбора обложки
    def pick_file(e):
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])  # только один файл

    # замена обложки
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            if config.cover_exists:
                # очистить src_base64 если у трека изначально есть обложка
                cover_image.src_base64 = None

            cover_image.src = e.files[0].path # показать новую обложку
            cover_image.opacity = 1
            edit_cover_icon.visible = False
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)



    def see_change_icon(e):
        if cover_image.src != "color/black.jpg":
            edit_cover_icon.visible = not edit_cover_icon.visible
            if cover_image.opacity != 0.5:
                cover_image.opacity = 0.5
            else:
                cover_image.opacity = 1
            page.update()

    cover_image = ft.Image(
        src="color/black.jpg",
        width=420,
        height=420,
        border_radius=30,
        opacity=0.5
    )

    # pops up when hovered on cover
    edit_cover_icon = ft.Container(
        content=ft.Image(
            src="icons/edit_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg",
            width=250,
            height=250,
            border_radius=30,
        ),
        alignment=ft.alignment.center,
        visible=True,
    )

    # если у трека есть обложка, то показать ее в cover_image
    if config.cover_exists:
        cover_image.src_base64=config.cover_exists
        cover_image.src=None
        cover_image.opacity=1

        edit_cover_icon.visible = False

    # song cover container
    song_cover = ft.Container(
        content=ft.Stack(
            controls=[cover_image, edit_cover_icon]
        ),
        width=420,
        height=420,
        border_radius=30,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e: pick_file(e),
        on_hover=lambda e: see_change_icon(e)
    )

    # song name
    song_name_input = ft.TextField(
        hint_text="Song name",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#EBD0E1"),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
        text_size=128,
        border_color="transparent",
        border_radius=30,
        bgcolor="transparent",
        width=1340,
    )

    if config.song_name_exists:
        song_name_input.hint_text = config.song_name_exists
        page.update()

    # artist name
    artist_name_input = ft.TextField(
        hint_text="Artist",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#EBD0E1"),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#EBD0E1"),
        text_size=64,
        border_color="transparent",
        border_radius=30,
        bgcolor="transparent",
        width=670,
    )

    if config.artist_name_exists:
        artist_name_input.hint_text = config.artist_name_exists
        page.update()

    # album name
    album_name_input = ft.TextField(
        hint_text="Album",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#EBD0E1"),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#EBD0E1"),
        text_size=64,
        border_color="transparent",
        border_radius=30,
        bgcolor="transparent",
        width=670,
    )

    if config.album_name_exists:
        album_name_input.hint_text = config.album_name_exists
        page.update()

    # редактировать название аудио в метаданных
    def edit_name_handl(e):
        # Если нет ID3-тэгов — создать
        try:
            audio = ID3(config.audio_file)
        except ID3NoHeaderError:
            audio = ID3()  # создаем теги, если их нет

        if song_name_input.value:
            audio.add(TIT2(encoding=3, text=song_name_input.value.strip())) # название трека в метаданных
        if artist_name_input.value:
            audio.add(TPE1(encoding=3, text=artist_name_input.value.strip())) # автор трека в метаданных
        if album_name_input.value:
            audio.add(TALB(encoding=3, text=album_name_input.value.strip()))

        if not cover_image.src_base64:
            # удаление старых обложек
            audio.delall("APIC")

        if cover_image.src:
            if not cover_image.src.endswith('black.jpg'): # временная заглушка
                # новая обложка
                with open(cover_image.src, "rb") as img_file:
                    audio.add(
                        APIC(
                            encoding=3,
                            mime="image/jpeg",
                            type=3,  # фронтальная обложка
                            desc="Cover",
                            data=img_file.read()
                        )
                    )

        audio.save(v2_version=3)

        apply_status_text.value = 'Done'
        page.update()
        time.sleep(1)
        apply_status_text.value = ' '
        page.update()

    # apply changes
    apply_button = ft.Stack(
        controls=[
            # visible button
            ft.FilledButton(
                ' ',
                bgcolor="#FE3C79",
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
                        color="#EBD0E1",
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
                on_click=lambda e: edit_name_handl(e),
            ),
        ],
    )

    def cancel_editing(e):
        config.cover_exists = None
        config.visible_edit_icon = True
        config.song_name_exists = None
        config.artist_name_exists = None
        config.album_name_exists = None
        page.go("/")

    # кнопка отмены
    cancel_button = ft.Stack(
        controls=[
            # border for visible button
            ft.FilledButton(
                ' ',
                bgcolor="#FE3C79",
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=255,
                height=50,
            ),

            # visible button
            ft.FilledButton(
                ' ',
                bgcolor="#EBD0E1",
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=250,
                height=45,
            ),

            # text on button
            ft.Container(
                content=ft.Text(
                    "Cancel",
                    style=ft.TextStyle(
                        color="#FE3C79",
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
                on_click=lambda e: cancel_editing(e),
            ),
        ],
        alignment=ft.alignment.center,
    )



    apply_status_text = ft.Text(
        ' ',
        style=ft.TextStyle(
            color="#EBD0E1",
            font_family="Gabarito",
            size=80,
            weight=ft.FontWeight.BOLD
        ),
    )

    apply_status = ft.Container(
        content=apply_status_text,
        alignment=ft.alignment.bottom_center
    )

    edit_page_ui = ft.Stack(
        controls=[
            apply_status,
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            song_cover,
                            ft.Column(
                                controls=[
                                    song_name_input,
                                    ft.Row(
                                        controls=[artist_name_input, album_name_input],
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),

                    ft.Row(
                        controls=[cancel_button, apply_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.START
            )
        ],
        expand=True,
    )

    background = ft.BoxDecoration(
        image=ft.DecorationImage(
            src="color/Desktop - 1.png",
            fit=ft.ImageFit.COVER
        )
    )

    return ft.View("/edit", controls=[edit_page_ui], bgcolor=ft.Colors.TRANSPARENT, decoration=background)