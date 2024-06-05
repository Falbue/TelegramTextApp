bot_api = ''
folder = 'data'
id_admin = 1
# -----------------------------------------------------------


import os
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
import re
from datetime import datetime
import pytz
import sys
import re
sys.path.append(folder)
import threading
bot = telebot.TeleBot(bot_api)


# пути
folder_path = f"{folder}"
db_name = "database.db"
db_path = os.path.join(folder_path, db_name)
texts_path = f"{folder}/texts"
menu_user_path = f'{folder}/user_menu'
menu_dev_path = f'{folder}/telegram_text_apps_menu'
error_path = f'{texts_path}/error_log.txt'

dev_menu = [
    {"name": "main", "text": 'Главное меню', 'buttons': {'Администратор': 'admin'}},
    {"name": "admin", "text": 'Панель администратора', 'back': 'main'},
]




# основные функции
def main_check():   # основные проверки
    if not os.path.exists(f"{folder}"):
        os.makedirs(f"{folder}")
        print("Папка библиотеки создана")
    if not os.path.exists(texts_path):
        os.makedirs(texts_path)
        print("Папка текстов создана")
    if not os.path.exists(menu_user_path):
        os.makedirs(menu_user_path)
        print("Папка с пользовательскими меню создана")
    if not os.path.exists(menu_dev_path):
        os.makedirs(menu_dev_path)
        print("Папка c меню приложения создана")     
    if not os.path.exists(error_path):
        with open(error_path, 'w'): 
            pass
        print("Файл с логами ошибок создан")
    if not os.path.exists(db_path):
        conn = sqlite3.connect(f"{folder}/database.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                user_id INTEGER,
                time_registration INTEGER,
                id_message INTEGER);
            ''')
        conn.close()
        print("База данных создана")

    create_dev_menu()

def now_time(): # получение текущего времени
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M")
    current_date = now_moscow.strftime("%m.%d.%Y")
    date = f"{current_date} {current_time}"
    return date

def create_menu(name=None, text=None, buttons=None, back=None, type_menu=None):
    print(f'Создано меню: {name}')
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'

    with open(path, 'w+', encoding='utf-8') as file:
        file.write(f'text: {text}\nbuttons: {buttons}\nback: {back}\ntype_menu: {type_menu}')

def create_dev_menu():
    for menu in dev_menu:
        create_menu(
            name=menu.get('name'), 
            text=menu.get('text'), 
            buttons=menu.get('buttons'), 
            back=menu.get('back')
        )

def open_data_menu(path): # получение всех данных из файла
    with open(path, encoding='utf-8') as file:
        file_data = file.read()
        data = {}
        for line in file_data.splitlines():
            key, value = line.split(': ', 1)
            data[key.strip()] = value.strip()
    return data

def open_menu(name = None, call = None, create = None): # открытие меню в чате из файла
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    # получение данных для меню
    if os.path.exists(path):
        data = open_data_menu(path)        
        text = None if isinstance(data['text'], str) and data['text'] == 'None' else data['text']
        buttons = None if isinstance(data['buttons'], str) and data['buttons'] == 'None' else data['buttons'].split(',')
        back = None if isinstance(data['back'], str) and data['back'] == 'None' else data['back']
        type_menu = None if isinstance(data['type_menu'], str) and data['type_menu'] == 'None' else data['type_menu']
    
    else:
        print(f"Меню {name} не найдено!")

    # изменение сообщения
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup = keyboard)
    except AttributeError: # этот код должен срабатывать, если в чате вообще нет сообщений
        bot.send_message(call.chat.id, text)
        bot.delete_message(chat_id=call.chat.id, message_id=call.message_id)


@bot.message_handler(commands=['start'])
def start(message): # обработка команды start
    message_id = message.id
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (message.chat.id,))
    result = c.fetchone()
    if result is None:
        registration = now_time()
        c.execute("INSERT INTO users (user_id, time_registration, id_message) VALUES (?, ?, ?)",
                  (message.chat.id, registration, message_id+1))
        conn.commit()
        print('Зарегистрирован новый пользователь', message.chat.id)
    else:
        c.execute(f"UPDATE users SET id_message = {(message_id+1)} WHERE user_id = {message.chat.id}")
        print('Пользователь' ,message.chat.id,'уже существует в базе')
        conn.commit()
        pass
    conn.close()

    open_menu('main', message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'data_start': 
        open_menu(name = 'main', call = call)

    

main_check()
print("Бот запущен...")

try:
    bot.polling()
except Exception as e:
    with open(error_path, 'w+', encoding='utf-8') as f:
        f.write(str(e) + "\n")
        goodbuy