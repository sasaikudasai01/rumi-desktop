import flet as ft
import flet_audio as fa
import os
import time
import json
import base64
import random

from pydantic.v1.datetime_parse import parse_time

import config
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter # для размытия изображения на фоне
from mutagen.id3 import ID3, APIC, TIT2, TPE1, ID3NoHeaderError, TALB # метаданные

def music_player(page: ft.Page):
    # border=ft.border.all(1, ft.Colors.RED), # отладка

    # список путей к мп3 файлам
    try:
        with open("mp3_files.json", "r", encoding="utf-8") as f:
            mp3_files_str = json.load(f)

        config.current_mp3_files = [Path(p) for p in mp3_files_str]
        config.all_mp3s = config.current_mp3_files.copy()
    except:
        config.current_mp3_files = None
        config.all_mp3s = None



    # добавить путь к аудио файлам
    add_path_icon = ft.Image(
        src=config.resource_path('icons/plus.svg'),
        width=420,
    )
    add_path = ft.Container(
        content=ft.Column(
            controls=[
                add_path_icon,

                ft.Text(
                    'Add audios',
                    style=ft.TextStyle(
                        color="#EBD0E1",
                        font_family="Gabarito",
                        size=55,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
        ink=True,
        on_click=lambda e: find_audio_files(e),
    )

    # кнопка добавить треки на странице где уже есть треки
    add_audio_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Image(
                    src=config.resource_path("icons/plus.svg"),
                    width=65,
                    height=65,
                    color='#EBD0E1'
                ),
                ft.Text(
                    'Add audios',
                    style=ft.TextStyle(
                        color="#EBD0E1",
                        font_family="Gabarito",
                        size=25,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            ]
        ),
        height=55,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e: find_audio_files(e),
        expand=True,
    )

    # элемент интерфейса с треками
    song_elements = ft.Column(
        controls=[],
        scroll='auto', # прокручивание страницы
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )

    # добавить треки на страницу
    def add_song_element_to_page(mp3_files_path):
        # если у трека есть обложка, название и артист, то показать всю инфy
        for file in mp3_files_path:
            cover_image = ft.Image(
                src=config.resource_path("color/icon_sq.png"),
            )

            # song cover container
            song_cover = ft.Container(
                content=cover_image,
                width=80,
                height=80,
                border_radius=25,
                alignment=ft.alignment.center,
                ink=True,
            )

            # song name
            song_name_text = ft.Text(
                'Song name',
                style=ft.TextStyle(
                    color="#FFFFFF",
                    font_family="Gabarito",
                    size=55,
                    weight=ft.FontWeight.BOLD,
                ),
                max_lines=1,  # ограничиваем одной строкой
                overflow=ft.TextOverflow.ELLIPSIS,  # добавит "..." если текст не влезает
                # чтобы overflow работал нужно в контейнере указать длину
            )

            song_name_container = ft.Container(
                content=song_name_text,
                expand=True,
            )

            # artist name
            artist_name_text = ft.Text(
                'Artist',
                style=ft.TextStyle(
                    color="#EBD0E1",
                    font_family="Gabarito",
                    size=55,
                    weight=ft.FontWeight.BOLD,
                ),
                max_lines=1,  # ограничиваем одной строкой
                overflow=ft.TextOverflow.ELLIPSIS,  # добавит "..." если текст не влезает
                # чтобы overflow работал нужно в контейнере указать длину
            )

            artist_name_container = ft.Container(
                content=artist_name_text,
                expand=True,
            )

            delete_icon = ft.Image(
                src=config.resource_path('icons/delete.svg'),
                opacity=0,
            )
            delete_song_button = ft.Container(
                content=delete_icon,
                width=80,
                height=80,
                ink=True,
                border_radius=25,
            )

            one_song_element = ft.Container(
                content=ft.Row(
                    controls=[
                        song_cover,
                        song_name_container,
                        artist_name_container,
                        delete_song_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    width=1380,
                    height=80,
                ),
            )

            try:
                # вывод информации о треках если есть
                try:
                    song = ID3(file)
                except ID3NoHeaderError:
                    song = ID3()  # создаем теги, если их нет

                for tag in song.values():
                    # есть ли у трека обложка
                    if isinstance(tag, APIC):
                        # конвертация в base64, чтобы использовать для обложки трека
                        cover_image.src = None
                        cover_image.src_base64 = base64.b64encode(tag.data).decode("utf-8")

                    # есть ли у трека название
                    if isinstance(tag, TIT2):
                        song_name_text.value = tag

                    # есть ли у трека артист
                    if isinstance(tag, TPE1):
                        artist_name_text.value = tag

                # добавление названия файла в название трека если в метаданных ничего нет
                if song_name_text.value == 'Song name':
                    # использовать название файла если в метаданных ничего нет
                    # file.stem возвращает название файла без расширения
                    song_name_text.value = str(file.stem)
                    artist_name_text.value = ''

                song_elements.controls.append(one_song_element)

                # передавать в функции данные отдельно, чтобы кнопки были уникальными
                song_cover.on_hover = lambda e, img=cover_image: see_change_icon(e, img)
                song_cover.on_click = lambda e, f=file: choose_audio_to_play(e, f)

                # передать путь к файлу и элемент интерфейса который нужно удалить
                delete_song_button.on_click = lambda _, delete_path=file, song_element=one_song_element: delete_song(delete_path, song_element)

                # сделать кнопку удалить видимой
                one_song_element.on_hover = lambda _, icon=delete_icon: show_delete_button(icon)

            except Exception as e:
                print(e)

        page.update()



    # удаление трека
    def delete_song(path, element):
        # нельзя удалить трек если он играет на данный момент
        if path == config.current_playing_audio:
            return

        # удаление элемента трека в интерфейсе
        song_elements.controls.remove(element)

        with open("mp3_files.json", "r", encoding="utf-8") as f:
            mp3_files_strr = json.load(f)

        mp3_files_strr.remove(str(path))
        config.current_mp3_files = [Path(fail) for fail in mp3_files_strr]

        mp3_files_path = [Path(p) for p in mp3_files_strr]

        # обновление списка путей
        with open("mp3_files.json", "w", encoding="utf-8") as f:
            json.dump([str(p) for p in mp3_files_path], f, ensure_ascii=False, indent=2)

        # если треков больше не осталось
        if not mp3_files_strr:
            os.remove('mp3_files.json')

            if config.previous_background:
                os.remove(config.previous_background)

            background_image.src = config.resource_path('color/Desktop - 1.png')
            config.previous_background = None
            profile_song_picture.src_base64 = None
            profile_song_picture.src = config.resource_path('color/icon_sq.png')
            background_image.opacity = 1

            song_elements.controls.append(add_path)
            add_audio_button.visible = False

        page.update()

    def show_delete_button(delete_icon):
        if delete_icon.opacity == 0:
            delete_icon.opacity = 1
        else:
            delete_icon.opacity = 0
        page.update()



    # добавить треки на страницу если переменная содержащая путь не пустая при первом запуске
    if config.current_mp3_files:
        add_song_element_to_page(config.current_mp3_files)
    else:
        song_elements.controls.append(add_path)
        add_audio_button.visible = False



    # окно выбора треков
    def find_audio_files(e):
        add_audios_picker.pick_files(allow_multiple=True, allowed_extensions=["mp3"])

    # сохранение пути к аудио файлам
    def find_audio_files_picked(e: ft.FilePickerResultEvent):
        if e.files:
            files = [Path(p.path) for p in e.files]

            # если функция споткнется на этом моменте значит add_path больше нет на странице
            # очень тупой костыль, но зато мне не нужно создавать новую функцию
            try:
                song_elements.controls.remove(add_path) # убрать кнопку добавить путь
                add_audio_button.visible = True

                config.current_mp3_files = files

                # сохранение в json
                with open("mp3_files.json", "a", encoding="utf-8") as f:
                    json.dump([str(p) for p in files], f, ensure_ascii=False, indent=2)

                add_song_element_to_page(config.current_mp3_files)

            except Exception as e:
                if str(e) == 'list.remove(x): x not in list':
                    new_paths = list(set(files) - set(config.current_mp3_files)) # есть ли новые треки

                    # добавить только если есть новые треки
                    if new_paths:
                        config.current_mp3_files.extend(Path(file) for file in files if file not in config.current_mp3_files)

                        # сохранение в json
                        with open("mp3_files.json", "w", encoding="utf-8") as f:
                            json.dump([str(p) for p in config.current_mp3_files], f, ensure_ascii=False, indent=2)

                        add_song_element_to_page(new_paths)

    add_audios_picker = ft.FilePicker(on_result=find_audio_files_picked)
    page.overlay.append(add_audios_picker)



    def see_edit_icon(e):
        if config.current_playing_audio:
            profile_song_edit_icon.visible = not profile_song_edit_icon.visible
            if profile_song_picture.opacity != 0.5:
                profile_song_picture.opacity = 0.5
            else:
                profile_song_picture.opacity = 1
            page.update()

    # перейти на страницу редактирования текущего трека
    def edit_current_song(_):
        if config.current_playing_audio:
            # остановить воспроизведение трека перед переходом на новую страницу
            audio1.pause()
            audio1.release()
            page.overlay.clear()
            page.update()



            # Если нет ID3-тэгов — создать
            try:
                song = ID3(config.current_playing_audio)
            except ID3NoHeaderError:
                song = ID3()  # создаем теги, если их нет

            for tag in song.values():
                # есть ли у трека обложка
                if isinstance(tag, APIC):
                    # конвертация в base64, чтобы использовать для обложки трека
                    config.cover_exists = base64.b64encode(tag.data).decode("utf-8")
                    ### для проверок ##############################################
                    # with open("cover.jpg", "wb") as f:
                    #    f.write(tag.data)

                # есть ли у трека название
                if isinstance(tag, TIT2):
                    config.song_name_exists = tag

                # есть ли у трека артист
                if isinstance(tag, TPE1):
                    config.artist_name_exists = tag

                # есть ли у трека название альбома
                if isinstance(tag, TALB):
                    config.album_name_exists = tag

            # сохранение пути
            config.audio_file = str(config.current_playing_audio)

            # удалить временный файл фона
            if config.previous_background:
                os.remove(config.previous_background)
                config.previous_background = None

            config.current_playing_audio = None

            page.go('/edit')
            page.update()

    # инфо о треке справа
    profile_song_edit_icon = ft.Container(
        content=ft.Image(
            src=config.resource_path("icons/edit_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            width=250,
            height=250,
            border_radius=30,
        ),
        alignment=ft.alignment.center,
        visible=False,
    )
    profile_song_picture = ft.Image(
        src=config.resource_path("color/icon_sq.png"),
        border_radius=25,
        opacity=1,
    )
    profile_song_picture_container = ft.Container(
        content=ft.Stack(
                controls=[profile_song_picture, profile_song_edit_icon,],
                alignment=ft.alignment.center,
        ),
        width=420,
        height=420,
        border_radius=25,
        alignment=ft.alignment.center,
        ink=True,
        on_hover=lambda e: see_edit_icon(e),
        on_click=lambda e: edit_current_song(e),
    )

    profile_song_name_text = ft.Text(
        'Song',
        style=ft.TextStyle(
            color="#FFFFFF",
            font_family="Gabarito",
            size=45,
            weight=ft.FontWeight.BOLD,
        ),
    )
    profile_artist_name_text = ft.Text(
        'Artist',
        style=ft.TextStyle(
            color="#EBD0E1",
            font_family="Gabarito",
            size=45,
            weight=ft.FontWeight.BOLD,
        ),
    )

    song_profile = ft.Column(
        controls=[profile_song_picture_container, profile_song_name_text, profile_artist_name_text],
        width=420,
        scroll='auto',  # прокручивание страницы
    )



    # затемнение ммини обложки трека
    def see_change_icon(e, img):
        if img.opacity != 0.5:
            img.opacity = 0.5
        else:
            img.opacity = 1
        page.update()

    # включение трека при нажатии на обложку
    def choose_audio_to_play(_, file):
        # если выбран тот же трек
        if audio1.src == file:
            play(_)
            return

        if config.current_playing_audio:
            audio1.pause()
            audio1.seek(0)

        audio1.src = file
        # один раз добавить аудио в оверлей
        if audio1 not in page.overlay:
            page.overlay.append(audio1)

        # вывод информации о треках в правом окне если есть
        try:
            temp_song_profile = ID3(file)
        except ID3NoHeaderError:
            temp_song_profile = ID3()  # создаем теги, если их нет

        ### для проверок #################################################
        #with open('temp_song_profile.txt', 'w', encoding='UTF-8') as txt:
        #    txt.write(f'temp_song_profile: {temp_song_profile}')

        # название трека
        profile_song_name_text.value = temp_song_profile.get('TIT2')
        # артист
        profile_artist_name_text.value = temp_song_profile.get('TPE1')
        # обложка
        cover_tag = None
        for key, tag in temp_song_profile.items():
            if key.startswith("APIC"):
                cover_tag = tag
                break

        if cover_tag:
            mime = cover_tag.mime  # формат картинки на обложке (png/jpeg)

            ### для проверок ############################################
            #print(f'mime: {mime}')
            #print("JPEG header:", cover_tag.data[:10])
            #print("Size:", len(cover_tag.data))

            #try:
            #    test_img = Image.open(io.BytesIO(cover_tag.data))
            #    print("Detected format:", test_img.format)
            #    print("Size:", test_img.size)
            #except Exception as ex:
            #    print("ERROR opening image:", ex)

            #img = Image.open(io.BytesIO(cover_tag.data))
            #print("Mode:", img.mode)
            #print("Info:", img.info)

            # определяем подходящий формат для Pillow для размытия на фон
            if mime == "image/jpeg":
                fmt = "JPEG"
            elif mime == "image/png":
                fmt = "PNG"
            else:
                fmt = "JPEG"

            # конвертация в base64, чтобы использовать для обложки трека
            profile_song_picture.src = None
            profile_song_picture.src_base64 = base64.b64encode(cover_tag.data).decode("utf-8")

            # установить обложку трека в качестве фона
            blurred_cover = blur_image_bytes(cover_tag.data, format=fmt, radius=5)
            with open(config.resource_path(f"color/temporal_blurred_{file.stem}.png"), "wb") as f:
                f.write(blurred_cover)

            background_image.src = config.resource_path(f"color/temporal_blurred_{file.stem}.png")
            if config.previous_background:
                os.remove(config.previous_background)
            config.previous_background = background_image.src

            background_image.opacity = 0.5

        else:
            if config.previous_background:
                os.remove(config.previous_background)

            background_image.src = config.resource_path('color/Desktop - 1.png')
            config.previous_background = None
            profile_song_picture.src_base64 = None
            profile_song_picture.src = config.resource_path('color/icon_sq.png')
            background_image.opacity = 1

        # добавление названия файла в название трека если в метаданных ничего нет
        if not profile_song_name_text.value:
            profile_song_name_text.value = str(os.path.basename(file).split('.')[0])

            profile_artist_name_text.value = ''

        config.current_playing_audio = file
        #page.update()

    # воспроизведение трека после загрузки
    def audio_loaded(_):
        audio_slider.value = 0
        audio_slider.max = audio1.get_duration()
        audio1.play()
        audio1.volume = volume_slider.value

        song_duration_text.value = ms_to_time(audio1.get_duration())

        page.update()

    # включение трека при нажатии на кнопку паузы
    def play(_):
        if audio1 in page.overlay:
            # если трек уже играет, то поставить на паузу
            if play_pouse_icon.src == config.resource_path("icons/pause_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"):
                audio1.pause()
            else:
                audio1.resume()
        page.update()

    # обновление позиции слайдера воспроизведения
    def audio_position_changed(_):
        if audio1.get_current_position():
            audio_slider.value=audio1.get_current_position()
            song_current_position_text.value = ms_to_time(audio1.get_current_position())
            page.update()

    # перемотка
    def slider_changed(e):
        if audio1 in page.overlay:
            audio1.seek(int(e.control.value))
            page.update()

    audio_slider = ft.Slider(
        min=0,
        on_change=slider_changed,
        active_color="#FE3C79",
        inactive_color="#EBD0E1",
    )

    # громкость
    def volume_slider_changed(_):
        if audio1 in page.overlay:
            audio1.volume = volume_slider.value

            if audio1.volume > 0.5:
                volume_icon.src = config.resource_path('icons/volume_up_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg')
            elif audio1.volume < 0.5:
                volume_icon.src = config.resource_path('icons/volume_down_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg')
            elif audio1.volume == 0:
                volume_icon.src = config.resource_path('icons/volume_off_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg')

            page.update()

    volume_slider = ft.Slider(
        min=0,
        max=1,
        value=1,
        on_change=volume_slider_changed,
        active_color="#FE3C79",
        inactive_color="#EBD0E1",
    )

    def volume_muter(_):
        if audio1 in page.overlay:
            # если громкость выше 0 то сделать мут и сохранить прошлую громкость
            if audio1.volume > 0:
                config.current_volume = audio1.volume
                audio1.volume = 0
                volume_slider.value = 0
                volume_icon.src = config.resource_path('icons/volume_off_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg')

            # вернуть громкость если трек в муте
            elif audio1.volume == 0:
                audio1.volume = config.current_volume
                volume_slider.value = config.current_volume
                volume_slider_changed(_)

            page.update()

    volume_icon = ft.Image(
        src=config.resource_path('icons/volume_up_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg'),
        width=45,
        height=45,
    )

    # поменять иконку воспроизведения
    def state_handler(_):
        # _.data -> playing
        # _.data -> paused
        # _.data -> completed

        if _.data == 'playing':
            play_pouse_icon.src = config.resource_path("icons/pause_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")

        elif _.data == 'paused':
            play_pouse_icon.src = config.resource_path("icons/play_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")

        elif _.data == 'completed':
            if config.play_mode == 'default':
                audio1.seek(0)
                play_pouse_icon.src = config.resource_path("icons/play_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg")
            else:
                next_track(_)

        page.update()

    audio1 = fa.Audio(
        on_loaded=lambda _: audio_loaded(_),
        on_position_changed=lambda e: audio_position_changed(e),
        on_state_changed=lambda e: state_handler(e),
    )

    play_pouse_icon = ft.Image(
        src=config.resource_path("icons/play_circle_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
        width=45,
        height=45,
    )
    play_pouse_button = ft.Button(
        content=play_pouse_icon,
        width=65,
        height=65,
        bgcolor=ft.Colors.TRANSPARENT,
        on_click=play,  # обработчик нажатия
    )

    def previous_track(_):
        if config.current_playing_audio:
            # перемотать трек на самое начало если он играет больше трех секунд
            if audio1.get_current_position() > 3000:
                audio1.seek(0)
                audio_slider.value = 0
                page.update()
                return

            if len(config.current_mp3_files) > 1:
                # индекс текущего трека в списке треков
                mp3_files_index = config.current_mp3_files.index(config.current_playing_audio)

                # если текущий трек самый первый в списке
                if mp3_files_index == 0:
                    # переключить на самый последний трек
                    previous_song = config.current_mp3_files[len(config.current_mp3_files) - 1]
                else:
                    # переключить на предыдущий
                    previous_song = config.current_mp3_files[mp3_files_index - 1]

                choose_audio_to_play(_, previous_song)

    def next_track(_):
        if config.current_playing_audio:
            if config.play_mode == 'default':
                if len(config.current_mp3_files) > 1:
                    # индекс текущего трека в списке треков
                    mp3_files_index = config.current_mp3_files.index(config.current_playing_audio)

                    # если текущий трек самый последний
                    if mp3_files_index == len(config.current_mp3_files) - 1:
                        # переключить на самый первый в списке
                        previous_song = config.current_mp3_files[0]
                    else:
                        # переключить на следующий
                        previous_song = config.current_mp3_files[config.current_mp3_files.index(config.current_playing_audio) + 1]
                    choose_audio_to_play(_, previous_song)
            else:
                current_play_mode_handl(_)

    # кнопка назад
    previous_icon = ft.Image(
        src=config.resource_path("icons/arrow_back_ios.svg"),
        width=25,
        height=25,
        color="#FE3C79",
    )
    previous_button = ft.Button(
        content=previous_icon,
        width=45,
        height=45,
        bgcolor=ft.Colors.TRANSPARENT,
        on_click=lambda e: previous_track(e),
    )

    # кнопка вперед
    next_icon = ft.Image(
        src=config.resource_path("icons/arrow_forward_ios.svg"),
        width=25,
        height=25,
        color="#FE3C79",
    )
    next_button = ft.Button(
        content=next_icon,
        width=45,
        height=45,
        bgcolor=ft.Colors.TRANSPARENT,
        on_click=lambda e: next_track(e),
    )

    def current_play_mode_handl(_):
        random.seed(time.time())

        if config.play_mode == 'repeat':
            audio1.seek(0)
            audio1.play()

        elif config.play_mode == 'shuffle':
            # временный список треков без текущего, чтобы выбрать следующий трек
            temp_list = config.current_mp3_files.copy()
            temp_list.remove(config.current_playing_audio)

            new_song_to_play = random.choice(temp_list)

            choose_audio_to_play(_, new_song_to_play)

        page.update()

    def current_play_mode_icon_handl(_, mode):
        if mode == 'repeat':
            if repeat_icon.color == "#EBD0E1":
                config.play_mode = 'repeat'
                repeat_icon.color = "#FE3C79" # сделать иконку повтора активной
            else:
                config.play_mode = 'default'
                repeat_icon.color = "#EBD0E1"

            shuffle_icon.color = "#EBD0E1"  # сделать иконку перемешивания неактивной

        elif mode == 'shuffle':
            if shuffle_icon.color == "#EBD0E1":
                config.play_mode = 'shuffle'
                shuffle_icon.color = "#FE3C79" # сделать иконку повтора активной
            else:
                config.play_mode = 'default'
                shuffle_icon.color = "#EBD0E1"

            repeat_icon.color = "#EBD0E1"  # сделать иконку повтора неактивной

        page.update()

    repeat_icon = ft.Image(
        src=config.resource_path("icons/repeat.svg"),
        width=45,
        height=45,
        color='#EBD0E1'
    )
    # кнопка повтор трека
    repeat_button = ft.Container(
        content=repeat_icon,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e, mode='repeat': current_play_mode_icon_handl(e, mode),
    )

    shuffle_icon = ft.Image(
        src=config.resource_path("icons/shuffle.svg"),
        width=45,
        height=45,
        color='#EBD0E1'
    )
    # кнопка повтор трека
    shuffle_button = ft.Container(
        content=shuffle_icon,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e, mode='shuffle': current_play_mode_icon_handl(e, mode),
    )

    # показать длительность трека
    def ms_to_time(ms: int) -> str:
        s = ms // 1000
        m = s // 60
        s = s % 60
        return f"{m}:{s:02}"

    song_duration_text = ft.Text(
        '0:00',
        style=ft.TextStyle(
            color="#EBD0E1",
            font_family="Gabarito",
            size=25,
            weight=ft.FontWeight.BOLD,
        ),
    )
    song_current_position_text = ft.Text(
        '0:00',
        style=ft.TextStyle(
            color="#EBD0E1",
            font_family="Gabarito",
            size=25,
            weight=ft.FontWeight.BOLD,
        ),
    )

    audio_controls = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        song_current_position_text,

                        ft.Container(
                            content=audio_slider,
                            alignment=ft.alignment.center,
                            expand=True,
                        ),

                        song_duration_text,

                        ft.Container(
                            content=volume_slider,
                            alignment=ft.alignment.center,
                        ),

                        ft.Container(
                            content=volume_icon,
                            width=45,
                            height=45,
                            border_radius=15,
                            alignment=ft.alignment.center,
                            ink=True,
                            on_click=lambda e: volume_muter(e),
                        ),
                    ],
                    spacing=0, # убрать расстояние между элементами
                ),

                ft.Row(
                    controls=[shuffle_button, previous_button, play_pouse_button, next_button, repeat_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=0, # убрать расстояние между элементами
        ),
    )



    # окно выбора аудио файла для перехода на страницу редактирования
    def pick_file(e):
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["mp3"])  # только один mp3 файл

    # сохранение пути к аудио файлу
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            edit_song = ID3(e.files[0].path)
            for edit_song_tag in edit_song.values():
                # есть ли у трека обложка
                if isinstance(edit_song_tag, APIC):
                    # конвертация в base64, чтобы использовать для обложки трека
                    config.cover_exists = base64.b64encode(edit_song_tag.data).decode("utf-8")

                # есть ли у трека название
                if isinstance(edit_song_tag, TIT2):
                    config.song_name_exists = edit_song_tag

                # есть ли у трека артист
                if isinstance(edit_song_tag, TPE1):
                    config.artist_name_exists = edit_song_tag

                # есть ли у трека название альбома
                if isinstance(edit_song_tag, TALB):
                    config.album_name_exists = edit_song_tag

            # сохранение пути
            config.audio_file = e.files[0].path

            # остановить воспроизведение трека перед переходом на новую страницу
            if audio1 in page.overlay:
                audio1.pause()
                audio1.release()
                page.overlay.clear()

            # удалить временный файл фона
            if config.previous_background:
                os.remove(config.previous_background)
                config.previous_background = None

            config.current_playing_audio = None

            page.go('/edit')
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # кнопка выбора аудиофайла / переход на страницу редактирования
    find_audio = ft.Container(
        content=ft.Image(
            src=config.resource_path("icons/edit_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            width=55,
            height=55,
        ),
        width=55,
        height=55,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e: pick_file(e),
    )



    def back_to_download_page(_):
        # очистить переменные перед переходом на новую страницу
        config.current_volume = None
        config.current_playing_audio = None

        # остановить воспроизведение трека перед переходом на новую страницу
        if audio1 in page.overlay:
            audio1.pause()
            audio1.release()
            page.overlay.clear()

        # удалить временный файл фона
        if config.previous_background:
            os.remove(config.previous_background)
            config.previous_background = None

        page.go("/")

    # кнопка "вернуться к странице скачивания"
    to_download_page_button = ft.Container(
        content=ft.Image(
            src=config.resource_path("icons/home_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg"),
            width=55,
            height=55,
            color='#EBD0E1'
        ),
        width=55,
        height=55,
        border_radius=15,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e: back_to_download_page(e),
    )



    def search_text_input_changed(_):
        # если поле пустое вернуть все треки
        if not search_text_input.value:
            song_elements.controls.clear()
            page.update()
            config.current_mp3_files = config.all_mp3s.copy()
            add_song_element_to_page(config.all_mp3s)
            return

    def search_text_input_submit(_):
        temporal_found_songs = []  # список найденных треков

        if config.current_mp3_files:
            for audio_file_path in config.all_mp3s:
                try:
                    temp_song_profile = ID3(audio_file_path)
                except ID3NoHeaderError:
                    temp_song_profile = ID3()  # создаем теги, если их нет

                # название трека
                temp_song_name_text = str(temp_song_profile.get('TIT2'))
                # артист
                temp_song_artist_name_text = str(temp_song_profile.get('TPE1'))

                # проверка на совпадение
                # совпадения по названию
                if search_text_input.value.lower() in temp_song_name_text.lower():
                    temporal_found_songs.append(audio_file_path)

                # совпадения по имени артиста
                elif search_text_input.value.lower() in temp_song_artist_name_text.lower():
                    temporal_found_songs.append(audio_file_path)

                # совпадения по названию файла если нет метаданных
                elif search_text_input.value.lower() in str(audio_file_path.stem.lower()):
                    temporal_found_songs.append(audio_file_path)

                # если совпадения есть
                if temporal_found_songs:
                    song_elements.controls.clear()
                    config.current_mp3_files = temporal_found_songs
                    add_song_element_to_page(temporal_found_songs)
                    page.update()
                else:
                    song_elements.controls.clear()
                    page.update()

    # поиск трека по названию
    search_text_input = ft.TextField(
        hint_text="Search song",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#40FE3C79"),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#FE3C79"),
        text_size=25,
        border_color="transparent",
        border_radius=15,
        bgcolor="#EBD0E1",
        on_submit=search_text_input_submit,
        on_change=search_text_input_changed,
    )



    # основная страница со всеми элементами
    music_player_page = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[to_download_page_button, find_audio]
                        ),
                        alignment=ft.alignment.top_center,
                    ),
                    ft.Column(
                        controls=[
                            ft.Row(controls=[add_audio_button, search_text_input,]),
                            song_elements
                        ],
                        expand=True,
                    ),
                    song_profile,
                ],
                expand=True,
            ),
            audio_controls
        ],
        expand=True, # нужно растянуть на весь экран чтобы внутренний Column мог прокручиваться
    )

    # функция для размытия изображения перед применением к фону
    def blur_image_bytes(input_bytes, format="JPEG", radius=20):
        image = Image.open(BytesIO(input_bytes))

        # jpeg не может работать с альфа каналом поэтому конвертация в rgb вместо rgba
        if image.mode in ("RGBA", "LA") and format.upper() in ("JPEG", "JPG"):
            image = image.convert("RGB")

        # нужно ресайзнуть картинку, чтобы блюр сработал адекватно
        # иначе при больших разрешениях блюр незаметен
        image = image.resize((640, 640), Image.LANCZOS)

        image = image.filter(ImageFilter.GaussianBlur(radius))

        output = BytesIO()
        image.save(output, format=format)
        return output.getvalue()



    background_image = ft.DecorationImage(
        src=config.resource_path("color/Desktop - 1.png"),
        fit=ft.ImageFit.COVER,
    )
    background = ft.BoxDecoration(
        image=background_image,
    )

    return ft.View("/music_player", controls=[music_player_page], bgcolor=ft.Colors.TRANSPARENT, decoration=background)