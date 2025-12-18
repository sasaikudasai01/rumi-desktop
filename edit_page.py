import flet as ft
import flet_audio as fa
import time
from flet.core.types import TextAlign
import config as cfg
from mutagen.id3 import ID3, APIC, TIT2, TPE1, ID3NoHeaderError, TALB # изменение метаданных трека
from mutagen import File

def edit_data(page: ft.Page):
    # окно выбора обложки
    def pick_file(e):
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])  # только один файл

    # замена обложки
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            if cfg.cover_exists:
                # очистить src_base64 если у трека изначально есть обложка
                cover_image.src_base64 = None

            cover_image.src = e.files[0].path # показать новую обложку
            cover_image.opacity = 1
            edit_cover_icon.visible = False
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)



    def see_change_icon(e):
        if cover_image.src != cfg.resource_path("color/icon_sq.png"):
            edit_cover_icon.visible = not edit_cover_icon.visible
            if cover_image.opacity != 0.5:
                cover_image.opacity = 0.5
            else:
                cover_image.opacity = 1
            page.update()

    cover_image = ft.Image(
        src=cfg.resource_path("color/icon_sq.png"),
        width=420,
        height=420,
        border_radius=30,
        opacity=0.5
    )

    # pops up when hovered on cover
    edit_cover_icon = ft.Container(
        content=ft.Image(
            src=cfg.resource_path("icons/edit_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            width=250,
            height=250,
            border_radius=30,
        ),
        alignment=ft.alignment.center,
        visible=True,
    )

    # если у трека есть обложка, то показать ее в cover_image
    if cfg.cover_exists:
        cover_image.src_base64=cfg.cover_exists
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
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
        text_size=128,
        border_color="transparent",
        border_radius=30,
        bgcolor="transparent",
        width=1340,
    )

    if cfg.song_name_exists:
        song_name_input.hint_text = cfg.song_name_exists
        page.update()

    # artist name
    artist_name_input = ft.TextField(
        hint_text="Artist",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_size=64,
        border_color="transparent",
        border_radius=30,
        bgcolor="transparent",
        width=670,
    )

    if cfg.artist_name_exists:
        artist_name_input.hint_text = cfg.artist_name_exists
        page.update()

    # album name
    album_name_input = ft.TextField(
        hint_text="Album",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color=cfg.not_main_color_hex),
        text_size=64,
        border_color="transparent",
        border_radius=30,
        bgcolor="transparent",
        width=670,
    )

    if cfg.album_name_exists:
        album_name_input.hint_text = cfg.album_name_exists
        page.update()

    # редактировать название аудио в метаданных
    def edit_name_handl(e):
        try:
            # это все нужно чтобы мутаген без проблем изменил метаданные
            play_pouse_icon.src = cfg.resource_path("icons/play_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")
            audio1.pause()
            audio1.seek(0)
            audio1.release()
            audio_slider.value=0
            page.overlay.remove(audio1)
            page.update()

            time.sleep(1)



            # Если нет ID3-тэгов — создать
            try:
                audio = ID3(cfg.audio_file)
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
                if not str(cover_image.src).endswith('icon_sq.png'): # временная заглушка
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

            audio.save(cfg.audio_file, v2_version=3)

            audio1.src = cfg.audio_file
            page.overlay.append(audio1)

            apply_status_text.value = 'Done'
            page.update()
            time.sleep(0.5)
            apply_status_text.value = ' '
            page.update()

        except Exception as e:
            print(e)

            cfg.errors_log(e, "Edit page")

            apply_status_text.value = 'Error'
            page.update()
            time.sleep(0.5)
            apply_status_text.value = ' '
            page.update()

    # apply changes
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
                on_click=lambda e: edit_name_handl(e),
            ),
        ],
    )



    # get metadata from spotify
    def get_spotify_metadata(_):
        try:
            song_name, artist_name, cover_path = cfg.return_metadata_from_spotify(song_name_input.value)

            if song_name:
                song_name_input.value = song_name

            if artist_name:
                artist_name_input.value = artist_name

            if cover_path:
                cover_image.src_base64 = None
                cover_image.src = cover_path
                if cover_image.opacity == 0.5:
                    see_change_icon(_)

            page.update()

        except Exception as e:
            print(e)

            cfg.errors_log(e, "get_spotify_metadata")

            apply_status_text.value = 'Error'
            page.update()
            time.sleep(0.5)
            apply_status_text.value = ' '
            page.update()

    dev_button = ft.Stack(
        controls=[
            # visible button
            ft.FilledButton(
                ' ',
                bgcolor=cfg.not_main_color_hex,
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=100,
                height=45,
            ),

            # get metadata from spotify
            ft.Container(
                content=ft.Text(
                    "dev",
                    style=ft.TextStyle(
                        color=cfg.main_color_hex,
                        font_family="Gabarito",
                        size=30,
                        weight=ft.FontWeight.BOLD
                    ),
                ),
                alignment=ft.alignment.center,
                width=100,
                height=45,
            ),

            # actual transparent button
            ft.FilledButton(
                ' ',
                bgcolor=ft.Colors.TRANSPARENT,
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=100,
                height=45,
                on_click=get_spotify_metadata,
            ),
        ],
    )



    def show_popup(_, sure):
        popup.visible = not popup.visible
        page.update()

        if sure == "sure":
            try:
                # это все нужно чтобы мутаген без проблем изменил метаданные
                play_pouse_icon.src = cfg.resource_path("icons/play_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")
                audio1.pause()
                audio1.seek(0)
                audio1.release()
                audio_slider.value=0
                page.overlay.remove(audio1)
                page.update()

                time.sleep(1)

                audio = File(cfg.audio_file)
                #if audio and audio.tags:
                audio.delete()

                cover_image.src = cfg.resource_path("color/icon_sq.png")
                cover_image.src_base64 = None
                cover_image.opacity = 0.5

                edit_cover_icon.visible = True

                song_name_input.hint_text = "Song name"
                song_name_input.value = ""

                artist_name_input.hint_text = "Artist name"
                artist_name_input.value = ""

                audio1.src = cfg.audio_file
                page.overlay.append(audio1)

                apply_status_text.value = 'Done'
                page.update()
                time.sleep(0.5)
                apply_status_text.value = ' '
                page.update()

            except Exception as e:
                print(e)

                cfg.errors_log(e, "Edit page. Trying to reset")

                apply_status_text.value = 'Error'
                page.update()
                time.sleep(0.5)
                apply_status_text.value = ' '
                page.update()

    reset_button = ft.Stack(
        controls=[
            # visible button
            ft.FilledButton(
                ' ',
                bgcolor=cfg.not_main_color_hex,
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=250,
                height=45,
            ),

            # text on button
            ft.Container(
                content=ft.Text(
                    "reset",
                    style=ft.TextStyle(
                        color=cfg.main_color_hex,
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
                on_click=lambda _, sure="show": show_popup(_, sure)
            ),
        ],
    )

    pretty_sure_button = ft.Stack(
        controls=[
            # visible button
            ft.FilledButton(
                ' ',
                bgcolor=cfg.not_main_color_hex,
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=180,
                height=45,
            ),

            # text on button
            ft.Container(
                content=ft.Text(
                    "Pretty sure",
                    style=ft.TextStyle(
                        color=cfg.main_color_hex,
                        font_family="Gabarito",
                        size=30,
                        weight=ft.FontWeight.BOLD
                    ),
                ),
                alignment=ft.alignment.center,
                width=180,
                height=45,
            ),

            # actual transparent button
            ft.FilledButton(
                ' ',
                bgcolor=ft.Colors.TRANSPARENT,
                style=ft.ButtonStyle(
                    shape=ft.ContinuousRectangleBorder(radius=60),
                ),
                width=180,
                height=45,
                on_click=lambda _, sure="sure": show_popup(_, sure),
            ),
        ],
        alignment=ft.alignment.center,
    )

    im_not_sure_button = ft.Stack(
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
                    "No",
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
                on_click=lambda _, sure="not_sure": show_popup(_, sure),
            ),
        ],
    )

    popup = ft.Stack(
        controls=[
            # background gradient
            ft.Container(
                gradient=ft.LinearGradient(
                    colors=[ft.Colors.with_opacity(0.9, color='#FF93D7'), ft.Colors.with_opacity(0.9, color='#56288C')],
                    stops=[0, 1],
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                ),
            ),

            ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            'This button deletes all metadata.\nAre you sure?',
                            style=ft.TextStyle(
                                color=cfg.not_main_color_hex,
                                font_family="Gabarito",
                                size=50,
                                weight=ft.FontWeight.BOLD,
                            ),
                            text_align=TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                    ),

                    ft.Container(
                        content=im_not_sure_button,
                        alignment=ft.alignment.center,
                    ),

                    ft.Container(
                        content=pretty_sure_button,
                        alignment=ft.alignment.center,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        expand=True,
        visible=False,
    )



    def cancel_editing(_, to_page):
        cfg.cover_exists = None
        cfg.visible_edit_icon = True
        cfg.song_name_exists = None
        cfg.artist_name_exists = None
        cfg.album_name_exists = None

        if any(isinstance(ctrl, fa.Audio) for ctrl in page.overlay):
            audio1.release()
            page.overlay.remove(audio1)
            page.update()
            time.sleep(0.5) # дать Flet время инициализировать компонент

        page.go(to_page)



    def audio_loaded(_):
        audio_slider.max = audio1.get_duration()

    def play(_):
        # есть ли какой-то трек на данный момент
        if not any(isinstance(ctrl, fa.Audio) for ctrl in page.overlay):
            page.overlay.append(audio1)
            page.update()
            time.sleep(0.5) # дать Flet время инициализировать компонент

        # если трек не играет, то включить
        if audio1.get_current_position() == 0:
            audio1.play()
            play_pouse_icon.src = cfg.resource_path("icons/pause_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")
            page.update()
            return

        # если трек уже играет, то поставить на паузу
        if play_pouse_icon.src == cfg.resource_path("icons/pause_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"):
            play_pouse_icon.src = cfg.resource_path("icons/play_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")
            audio1.pause()
        else:
            play_pouse_icon.src = cfg.resource_path("icons/pause_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")
            audio1.resume()
        page.update()

    def audio_position_changed(_):
        if audio1.get_current_position():
            audio_slider.value=audio1.get_current_position()
            page.update()

    def slider_changed(e):
        audio1.seek(int(e.control.value))
        page.update()

    audio_slider = ft.Slider(
        min=0,
        on_change=slider_changed,
        active_color=cfg.main_color_hex,
        inactive_color=cfg.not_main_color_hex,
    )

    audio1 = fa.Audio(
        src=cfg.audio_file,
        on_loaded=lambda _: audio_loaded(_),
        on_position_changed=lambda e: audio_position_changed(e),
    )

    page.overlay.append(audio1)

    play_pouse_icon = ft.Image(
        src=cfg.resource_path("icons/play_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
        color=cfg.not_main_color_hex,
        width=60,
        height=60
    )
    play_pouse_button = ft.Button(
        content=play_pouse_icon,
        width=65,
        height=65,
        bgcolor=ft.Colors.TRANSPARENT,
        on_click=play,  # обработчик нажатия
    )

    audio_controls = ft.Row(
        controls=[
            ft.Container(
                content=play_pouse_button
            ),
            ft.Container(
                content=audio_slider,
                width=840,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )



    apply_status_text = ft.Text(
        ' ',
        style=ft.TextStyle(
            color=cfg.not_main_color_hex,
            font_family="Gabarito",
            size=80,
            weight=ft.FontWeight.BOLD
        ),
    )

    apply_status = ft.Container(
        content=apply_status_text,
        alignment=ft.alignment.bottom_center
    )



    # кнопка "вернуться к странице скачивания"
    to_download_page_button = ft.Container(
        content=ft.Image(
            src=cfg.resource_path("icons/home_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            width=55,
            height=55,
            color=cfg.not_main_color_hex
        ),
        width=55,
        height=55,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda _, to_page="/": cancel_editing(_, to_page),
    )



    music_library_button = ft.Container(
        content=ft.Image(
            src=cfg.resource_path("icons/library_music_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            color=cfg.not_main_color_hex,
            width=55,
            height=55,
        ),
        width=55,
        height=55,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda _, to_page="/music_player": cancel_editing(_, to_page),
    )

    edit_page_ui = ft.Stack(
        controls=[
            apply_status,
            ft.Row(
                controls=[to_download_page_button, music_library_button]
            ),
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

                    audio_controls,

                    ft.Row(
                        controls=[dev_button, reset_button, apply_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            popup,
        ],
        expand=True,
    )

    background = ft.BoxDecoration(
        image=ft.DecorationImage(
            src=cfg.wallpaper,
            fit=ft.ImageFit.COVER
        )
    )



    # управление на клавиатуре
    def make_fullscreen(e: ft.KeyboardEvent):
        # полноэкранный режим
        if e.key == "F11":
            page.window.full_screen = not page.window.full_screen
            page.update()

    page.on_keyboard_event = make_fullscreen



    return ft.View("/edit", controls=[edit_page_ui], bgcolor=ft.Colors.TRANSPARENT, decoration=background)