import re
import json
import sys, os
from datetime import datetime

# работа с иконками
def resource_path(relative_path):
    # если ето экзешник
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # если запуск из проекта
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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



# существует ли user_setting.json
if os.path.exists("user_setting.json"):
    with open ("user_setting.json", "r", encoding="UTF-8") as f:
        user_settings = json.load(f) # загруженные настройки пользователя

        try:
            # существует ли файл
            if os.path.exists(user_settings["wallpaper_path"]):
                # расширение файла
                wallpaper_format = user_settings["wallpaper_path"].split('.')[1]
                # проверка расширения файла
                if wallpaper_format in ['png', 'jpg', 'jpeg']:
                    wallpaper = user_settings["wallpaper_path"]

        except Exception as e:
            print(e)

            # сохранение ошибки
            with open('errors.log', 'a', encoding='utf-8') as log:
                log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Loading settings) {str(e)}\n')

def is_hex_color(s):
    return bool(re.fullmatch(r"#([0-9a-fA-F]{6})", s))

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



# сохранение ошибки
def errors_log(error, caused_page):
    with open('errors.log', 'a', encoding='utf-8') as logs:
        logs.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ({caused_page}) {str(error)}\n')