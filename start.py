import flet as ft
import time
import base64
import config
from yt_dlp import YoutubeDL
from PIL import Image # редактирование изображения
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TPE1, TALB # изменение метаданных трека
import os

import json

def startview(page: ft.Page):
    # вырезать офишал музик видео из названия
    def skobki_remove(title):
        skobki_sq = []  # список квадратных скобок
        skobki_c = []  # список круглых скобок
        title_final_name = title  # название файла после удаления скобок

        # получение текста в скобках если есть скобки
        while '(' in title_final_name or '[' in title_final_name:
            try:
                if '(' in title_final_name:
                    skobka = title_final_name.split('(')[1].split(')')[0]
                    skobki_c.append(skobka)
                    title_final_name = title_final_name.replace(f'({skobka})', '').strip()
                if '[' in title_final_name:
                    skobka = title_final_name.split('[')[1].split(']')[0]
                    skobki_sq.append(skobka)
                    title_final_name = title_final_name.replace(f'[{skobka}]', '').strip()
            except:
                pass

        replacements = ['official', 'video', 'lyrics',
                        'lyric', 'color', 'hd', 'live',
                        'remaster', 'audio', 'original',
                        'ost', 'soundtrack', 'remastered', 'hq']

        title_final_name = title  # вернуть полное название
        for replacement in replacements:
            for skobka_sq in skobki_sq:
                # эта проверка нужна, чтобы функция была универсальной, иначе пришлось бы сравнивать каждый вариант вручную, учитывая все варианты заглавных букв
                if replacement in skobka_sq.lower():
                    title_final_name = title_final_name.replace(f'[{skobka_sq}]', '').strip()
            for skobka_c in skobki_c:
                if replacement in skobka_c.lower():
                    title_final_name = title_final_name.replace(f'({skobka_c})', '').strip()

        return title_final_name

    # сделать квадратную картинку для трека
    def mp3_thumbnail(change_img, image_path, audio_path, audio_name, channel_name):
        if '- Topic' in channel_name:
            channel_name = channel_name.replace('- Topic', '').strip()

        audio = MP3(audio_path, ID3=ID3)
        # создание ID3-тэгов если их нет
        try:
            audio.add_tags()
        except error:
            pass

        if change_img:
            im = Image.open(image_path)  # объект изображения с параметрами
            width, height = im.size  # разрешение изображения
            min_side = min(width, height)  # выбор минимальной стороны изображения

            # центрируем квадратную обрезку
            left = (width - min_side) / 2
            top = (height - min_side) / 2
            right = (width + min_side) / 2
            bottom = (height + min_side) / 2

            new_image_path = image_path.split('.')[0]

            im_cropped = im.crop((left, top, right, bottom))
            im_cropped.save(f"{new_image_path}.jpg", "JPEG")
            os.remove(image_path)  # удаление оригинального изображения после изменения соотношения сторон

            # добавление обложки к аудио файлу
            with open(f"{new_image_path}.jpg", 'rb') as albumart:
                audio.tags.add(
                    APIC(
                        encoding=3,  # utf-8
                        mime='image/jpeg',  # или 'image/png'
                        type=3,  # front cover
                        desc='Cover',
                        data=albumart.read()
                    )
                )
            # принудительное сохранение файла в ID3v2.3
            audio.tags.add(TIT2(encoding=3, text=audio_name))  # название трека в метаданных
            audio.tags.add(TPE1(encoding=3, text=channel_name))  # автор трека в метаданных
            audio.save(
                v2_version=3)  # по умолчанию файл имеет только ID3v1, поэтому mutagen обрабатывает его некорректно
            os.remove(f"{new_image_path}.jpg")  # удаление обложки после применения к аудио файлу

    def download_yt(e, yt_format, download_img):
        popup.visible = not popup.visible

        if (text_input.value.startswith('https://youtu.be/') or
            text_input.value.startswith('https://www.youtube.com/watch?') or
            text_input.value.startswith('https://youtube.com/playlist?')):
            pass
        else:
            return

        download_status_text.value = f'Downloading...'
        page.update()

        is_no_playlist = True  # плейлист ли это
        #download_img = True  # скачать обложку для трека
        url = text_input.value  # ссылка на ютуб видео

        if url.startswith('https://youtu.be/'):  # работа с укороченными ссылками
            text = url.replace('https://youtu.be/', '')
            url = text.split('?')[0].strip()  # ссылка на ютуб видео
        elif 'playlist?' in url:  # плейлист ли это
            is_no_playlist = False
            if not url.startswith('https://www.youtube.com/'):  # поменять ссылку
                text = url.replace('https://', 'https://www.')
                url = text.split('&si')[0].strip()  # нормальная ссылка на плейлист

        # если пользователь хочет скачать аудио
        if yt_format == 'mp4':
            ydl_opts_format = 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4][vcodec^=avc1]'  # попытка получить лучшее видео и аудио в mp4
            ydl_opts_postprocessors = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'  # Перекодирует финальный файл
            }]
            ydl_opts_outtmpl = 'video'
            ydl_opts_merge_output_format = 'mp4'
            download_img = False
        else:
            ydl_opts_format = 'bestaudio/best'
            ydl_opts_postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # формат аудио
                'preferredquality': '192',  # качество после кодирования
            }]
            ydl_opts_outtmpl = 'music'



        def my_hook(d):
            # status: finished
            # status: downloading
            if is_no_playlist:
                download_status_text.value = f'Downloading {d["_percent_str"]}'
            else:
                if d["status"] == 'finished':
                    config.video_counter += 1
                download_status_text.value = f'Video [{config.video_counter}] {d["_percent_str"]}'
            page.update()
            ### для проверок ##############################################
            #with open("progress_log.json", "a", encoding="utf-8") as f:
            #    json.dump(d, f, ensure_ascii=False, indent=2)



        # параметры для скачиваемого аудио
        ydl_opts = {
            'format': ydl_opts_format,  # качество аудио
            'writethumbnail': download_img,
            'outtmpl': f'{config.download_path}/%(title)s.%(ext)s',  # название
            'restrictfilenames': True,  # избавление от лишних символов в названии
            'writedescription': False,  # не скачивать описание видео
            'writeannotations': False,  # не скачивать аннотации
            'writeplaylistmetafiles': False,  # не скачивать метаданные плейлиста
            'postprocessors': ydl_opts_postprocessors,
            'noplaylist': is_no_playlist,
            'cookiefile': 'cookies.txt',
            'quiet': True,
            'progress_hooks': [my_hook],
        }
        if yt_format == 'mp4':
            ydl_opts['merge_output_format'] = ydl_opts_merge_output_format

        if download_img:  # конвертировать изображение если есть
            ydl_opts['convertthumbnails'] = 'webp'

        try:
            with YoutubeDL(ydl_opts) as ydl:
                yt_video_info = ydl.extract_info(url, download=True)
                ### для проверок ###################################
                # sanitized = ydl.sanitize_info(temp_info)
                #with open("info.json", "w", encoding="utf-8") as f:
                #   json.dump(sanitized, f, ensure_ascii=False, indent=2)

            # если это плейлист, то ydl возвращает список словарей entries
            if 'entries' in yt_video_info:  # проверка плейлист ли это
                for entry in yt_video_info['entries']:
                    if entry is None:
                        continue  # иногда бывают пустые entry

                    # внутри каждого entry есть ключ requested_downloads (список словарей с одним элементом), который содержит путь к файлу filepath
                    for requested_download in entry['requested_downloads']:
                        file_path = requested_download['filepath'].replace('\\', '/')  # путь к файлу

                        if '(' or '[' in entry['title']:
                            mp34_filename = skobki_remove(entry['title'])
                        else:
                            mp34_filename = entry['title']

                        if yt_format == 'mp3':
                            # изменение метаданных трека
                            mp3_thumbnail(download_img, file_path.replace('mp3', 'webp'), file_path, mp34_filename, entry['channel'])

                if download_img:
                    # удаление обложки плейлиста
                    for info in yt_video_info['thumbnails']:
                        if 'filepath' in info:
                            os.remove(info["filepath"].replace('\\', '/'))

            else:
                for requested_download in yt_video_info['requested_downloads']:
                    file_path = requested_download['filepath'].replace('\\', '/')  # путь к файлу

                    if '(' or '[' in yt_video_info['title']:
                        mp34_filename = skobki_remove(yt_video_info['title'])
                    else:
                        mp34_filename = yt_video_info['title']

                    if yt_format == 'mp3':
                        # изменение метаданных трека
                        mp3_thumbnail(download_img, file_path.replace('mp3', 'webp'), file_path, mp34_filename, yt_video_info['channel'])

            download_status_text.value = 'Finished'
            page.update()
            time.sleep(10)
            download_status_text.value = ' '
            page.update()

            config.video_counter = 0

        except Exception as e:
            print(f'Error: {e}')

    # поле ввода ссылки
    text_input = ft.TextField(
        hint_text="url",
        hint_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#40FE3C79"),
        text_style=ft.TextStyle(font_family="Gabarito", weight=ft.FontWeight.BOLD, color="#FE3C79"),
        text_size=45,
        border_color="transparent",
        border_radius=80,
        bgcolor="transparent",
    )
    search_field = ft.FilledButton(
        ' ',
        bgcolor="#EBD0E1",
        style=ft.ButtonStyle(
            shape=ft.ContinuousRectangleBorder(radius=60),
        ),
        width=900,
        height=80,
    )

    # иконка поиска
    search_icon = ft.Image(
        src="icons/search_24dp_220918_FILL0_wght400_GRAD0_opsz24.svg",
        width=60,
        height=60,
        color="#FE3C79",
    )



    # окно выбора пути скачивания
    def directory_path(e):
        # если ничего не скачивается на данный момент
        if download_status_text.value == ' ':
            # ввел ли пользователь ссылку
            if text_input.value:
                directory_picker.get_directory_path()

    # сохранение пути к аудио файлу
    def on_directory_picked(e: ft.FilePickerResultEvent):
        config.download_path = e.path
        toggle_menu(page)

    directory_picker = ft.FilePicker(on_result=on_directory_picked)
    page.overlay.append(directory_picker)

    # show download menu
    def toggle_menu(e):
        if config.download_path:
            popup.visible = not popup.visible
            page.update()

    download_button = ft.FilledButton(
        content=ft.Image(
            src="icons/download_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg",
            width=60,
            height=60,
        ),
        width=80,
        height=80,
        bgcolor="#FE3C79",
        style=ft.ButtonStyle(
            shape=ft.ContinuousRectangleBorder(radius=60),
        ),

        on_click=directory_path  # обработчик нажатия
    )

    # кнопка скачивания аудио
    mp3_button = ft.Stack(
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
                    "Audio",
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
                on_click=lambda e: download_yt(e, "mp3", False),
            ),
        ],
    )

    mp3_with_cover_button = ft.Stack(
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
                    "Audio (cover)",
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
                on_click=lambda e: download_yt(e, "mp3", True),
            ),
        ],
    )

    # кнопка скачивания видео
    mp4_button = ft.Stack(
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
                    "Video",
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
                on_click=lambda e: download_yt(e, "mp4", False),
            ),
        ],
    )

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
                on_click=toggle_menu,
            ),
        ],
        alignment=ft.alignment.center,
    )

    # pop up с менюшкой выбора формата
    popup = ft.Stack(
        controls=[
            # background gradient
            ft.Container(
                gradient=ft.LinearGradient(
                    colors=[ft.Colors.with_opacity(0.5, color='#FF93D7'), ft.Colors.with_opacity(0.5, color='#56288C')],
                    stops=[0, 1],
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                )
            ),

            # download buttons
            ft.Column(
                controls=[
                    ft.Container(
                        content=mp3_button,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=mp3_with_cover_button,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=mp4_button,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=cancel_button,
                        alignment=ft.alignment.center,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        expand=True,
        visible=False,
    )

    # окно выбора аудио файла
    def pick_file(e):
        if download_status_text.value == ' ':
            file_picker.pick_files(allow_multiple=False, allowed_extensions=["mp3"])  # только один mp3 файл

    # сохранение пути к аудио файлу
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            song = ID3(e.files[0].path)
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
            config.audio_file = e.files[0].path
            page.go('/edit')
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    # кнопка выбора аудиофайла
    find_audio = ft.Container(
        content=ft.Image(
            src="icons/edit_24dp_EBD0E1_FILL0_wght400_GRAD0_opsz24.svg",
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



    download_status_text = ft.Text(
        ' ',
        style=ft.TextStyle(
            color="#EBD0E1",
            font_family="Gabarito",
            size=80,
            weight=ft.FontWeight.BOLD
        ),
    )

    download_status = ft.Container(
        content=download_status_text,
        alignment=ft.alignment.bottom_center
    )

    main_page = ft.Stack(
        controls=[
            download_status,
            # Центральный блок: поле ввода + кнопка
            ft.Row(
                controls=[
                    ft.Stack(
                        controls=[
                            # Нижний TextField — для отображения фона, бордюров
                            search_field,
                            ft.Container(
                                content=search_icon,
                                alignment=ft.alignment.center_right,
                                padding=ft.padding.only(right=10),
                            ),
                            # настоящий ввод текста
                            ft.Container(
                                content=text_input,
                                alignment=ft.alignment.center_left,
                                width=840,
                            ),
                        ],
                        width=900,
                        height=80
                    ),
                    ft.Container(
                        content=download_button,
                        alignment=ft.alignment.center,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            popup,
            find_audio,
        ],
        expand=True,
    )

    background = ft.BoxDecoration(
        image=ft.DecorationImage(
            src="color/Desktop - 1.png",
            fit=ft.ImageFit.COVER
        )
    )

    return ft.View("/", controls=[main_page], bgcolor=ft.Colors.TRANSPARENT, decoration=background)