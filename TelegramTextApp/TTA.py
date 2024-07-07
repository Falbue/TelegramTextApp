import os
import subprocess

def start():
    # Определяем директорию, в которой находится скрипт
    base_directory = os.path.dirname(os.path.abspath(__file__))

    # Проходим по всем элементам в указанной директории
    for item in os.listdir(base_directory):
        item_path = os.path.join(base_directory, item)
        
        # Проверяем, является ли элемент папкой
        if os.path.isdir(item_path):
            bot_script_path = os.path.join(item_path, 'bot.py')
            
            # Проверяем, существует ли скрипт bot.py в этой папке
            if os.path.exists(bot_script_path):
                print(f"Запуск скрипта {bot_script_path}")
                # Запускаем скрипт bot.py
                subprocess.run(['python', bot_script_path])

