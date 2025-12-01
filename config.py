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
play_mode = 'default'



import sys, os
# работа с иконками
def resource_path(relative_path):
    # Если программа запакована в EXE
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # Обычный запуск из проекта
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



#pyinstaller -w ^
#-i color/icon_sq.ico ^
#--add-data "color;color" ^
#--add-data "icons;icons" ^
#--add-data "cooks;cooks" ^
#main.py