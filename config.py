import re
import json
import sys, os
from datetime import datetime
import requests
import base64
from dotenv import load_dotenv
from pathlib import Path
import shutil



# есть ли ffmpeg в PATH
ffmpeg_is_in_path = False

system_path = os.environ.get("PATH", "")
system_path_list = [Path(path) for path in system_path.split(os.pathsep)]

for path in system_path_list:
    folders = list(path.parts)
    if len(folders) >= 2:
        pre_last = folders[-2]
        last = folders[-1]
        if (pre_last, last) == ("ffmpeg", "bin"):
            print(f'path: "{path}"')
            ffmpeg_is_in_path = True



if getattr(sys, "frozen", False):
    # запускается из exe
    base_dir = Path(sys.executable).parent
else:
    # запускается из скрипта
    base_dir = Path(__file__).parent

# работа с путями для создания файлов/папок в основной директории
def base_dir_files(file_name):
    return Path(base_dir) / file_name

# работа с путями для создания файлов в папке в основной директории
def base_dir_folder_file(folder, file_name):
    return Path(base_dir) / folder / file_name



load_dotenv(Path(base_dir) / ".env")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")



temporal_dir = base_dir_files("temporal")

if temporal_dir.exists():
    try:
        shutil.rmtree(temporal_dir)
    except FileNotFoundError:
        pass



# работа с иконками
def resource_path(relative_path):
    # если ето экзешник
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # если запуск из проекта
        base_path = os.path.abspath(".")

    return str(Path(base_path) / relative_path)

# дефолт значения настроек
user_settings = {} # пустая переменная для настроек пользователя
wallpaper = resource_path("color/Desktop - 1.png")
main_color_hex = "#FE3C79" # основной цвет интерфейса
not_main_color_hex = "#EBD0E1" # второстепенный цвет элементов интерфейса

audio_file = None # путь к аудио для редактирования

download_path = None # путь для скачивания

video_counter = 0 # количество скачанных видео из плей листа

cover_exists = None # есть ли у трека для редактирования обложка
song_name_exists = None # есть ли у трека название
artist_name_exists = None # есть ли у трека артист
album_name_exists = None # есть ли у трека название альбома

current_volume = None # какая была громкость до мута
current_playing_audio = None # какой трек играет на данный момент
previous_background = None # прошлый фон
current_mp3_files = [] # список загруженных треков на данный момент. НЕ ДОЛЖЕН быть None
all_mp3s = [] # список всех треков
play_mode = 'default'

# не ищет ли пользователь на данный момент трек, чтобы правильно отрабатывать нажатие на пробел
focus_on_search_text_input = False

# active_color элементы у которых меняется параметр active_color на main_color_hex
# inactive_color элементы у которых меняется параметр inactive_color на not_main_color_hex
# color_main элементы у которых меняется параметр color на main_color_hex
# color_not_main элементы у которых меняется параметр color на not_main_color_hex
dynamic_color = {"active_color": [], "inactive_color": [], "color_main": [], "color_not_main": []} # элементы с динамичным цветом



# сохранение ошибки
def errors_log(error, caused_page):
    with open(base_dir_files("errors.log"), 'a', encoding='utf-8') as logs:
        logs.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ({caused_page}) {str(error)}\n')



# существует ли user_setting.json
if os.path.exists(base_dir_files("user_setting.json")) and os.path.getsize("user_setting.json") > 0:
    try:
        with open(base_dir_files("user_setting.json"), "r", encoding="UTF-8") as f:
            user_settings = json.load(f)  # загруженные настройки пользователя

        wallpaper_path = user_settings.get("wallpaper_path")

        if wallpaper_path:
            if os.path.exists(base_dir_files(user_settings["wallpaper_path"])):
                # расширение файла
                wallpaper_format = user_settings["wallpaper_path"].split('.')[1]
                # проверка расширения файла
                if wallpaper_format in ['png', 'jpg', 'jpeg']:
                    wallpaper = user_settings["wallpaper_path"]

    except Exception as e:
        print(e)

        # сохранение ошибки
        errors_log(e, "Loading settings")

def is_hex_color(color):
    return bool(re.fullmatch(r"#([0-9a-fA-F]{6})", color))

if "main_color_hex" in user_settings.keys():
    if user_settings["main_color_hex"].lower() != "default":
        hex_color = user_settings["main_color_hex"]

        if is_hex_color(hex_color):
            main_color_hex = user_settings["main_color_hex"]

if "not_main_color_hex" in user_settings.keys():
    if user_settings["not_main_color_hex"].lower() != "default":
        hex_color = user_settings["not_main_color_hex"]

        if is_hex_color(hex_color):
            not_main_color_hex = user_settings["not_main_color_hex"]



# настройки
def open_settings(_, page):
    page.go('/settings')



# get metadata from spotify
def return_metadata_from_spotify(url):
    resp_status_code = ''
    resp_text = ''
    try:
        auth = base64.b64encode(
            f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()
        ).decode()

        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        )

        resp_status_code = resp.status_code
        resp_text = resp.text

        token = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        ).json()["access_token"]

        if bool(re.fullmatch(r"[0-9a-zA-Z]{22}", url)):
            track_id = url  # из ссылки
        elif url.startswith("https://open.spotify.com/track/"):
            track_id = url.split("https://open.spotify.com/track/")[1]
            track_id = track_id.split("?")[0]
        else:
            return

        track = requests.get(
            f"https://api.spotify.com/v1/tracks/{track_id}",
            headers={"Authorization": f"Bearer {token}"}
        ).json()

        track_name = track.get("name")

        # track["artists"] это словари которые хранят всю инфу об исполнителе / исполнителях
        artists_list = [a["name"] for a in track["artists"]]
        artists_str = ", ".join(artist.strip() for artist in artists_list)

        cover_url = track["album"]["images"][0]["url"]

        sanitized_cover_name = re.sub(r'[\\/:*?"<>|]', '_', f'{track_name} - {artists_str}.jpg')

        temporal_dir.mkdir(parents=True, exist_ok=True)
        cover_path = temporal_dir / sanitized_cover_name

        resp = requests.get(cover_url, timeout=10)
        resp.raise_for_status()

        with open(cover_path, "wb") as f:
            f.write(resp.content)

        return track_name, artists_str, cover_path

    except Exception as e:
        print(e)
        err = str(e)
        if str(e) == "'access_token'":
            print(f'{str(e)}. Invalid client_id or client_secret. STATUS: {resp_status_code}. {resp_text}')
            err = f'{str(e)}. Invalid client_id or client_secret. STATUS: {resp_status_code}. {resp_text}'

        elif str(e) == "'client_id'":
            print(f"{str(e)}. Failed to get client_id or client_secret")
            err = f"{str(e)}. Failed to get client_id or client_secret"

        errors_log(err, "Tried to get Spotify metadata")