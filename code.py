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
    {"name": "main", "text": 'Главное меню'},
    {"name": "admin", "text": 'Панель администратора', 'buttons': {'Настройка меню': 'admin_settings-menu'}, 'back': 'main'},
    {"name": "settings-menu", "text": 'Найстройки меню', 'buttons': {'Редактировать': 'admin_edit_menu', 'Создать': 'admin_create-menu', 'Удалить': 'admin_delete-menu'}, 'back': 'admin'},
    {"name": "create-menu", "text": 'Введите название меню', 'back': 'settings-menu', 'type_menu': 'insert_text', 'command': 'create_menu'},
    {"name": "delete-menu", "text": 'Выберите меню для удаления', 'buttons': {'menu_lists': 'admin_delete'}, 'back': 'settings-menu'},
]




# основные функции
def main_check(): # основные проверки
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

def create_menu(name=None, text=None, buttons=None, back=None, type_menu=None, command=None): # создание меню
    print(f'Создано меню: {name}')
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'

    with open(path, 'w+', encoding='utf-8') as file:
        file.write(f'text: {text}\nbuttons: {buttons}\nback: {back}\ntype_menu: {type_menu}\ncommand: {command}')

def create_dev_menu(): # создание меню программы
    for menu in dev_menu:
        create_menu(
            name=menu.get('name'), 
            text=menu.get('text'), 
            buttons=menu.get('buttons'), 
            back=menu.get('back'),
            type_menu=menu.get('type_menu'),
            command=menu.get('command'),
        )

def open_data_menu(path): # получение всех данных из файла
    with open(path, encoding='utf-8') as file:
        file_data = file.read()
        data = {}
        for line in file_data.splitlines():
            key, value = line.split(': ', 1)
            data[key.strip()] = value.strip()
    return data

def create_keyboard(buttons, back): # создание клавиатуры
    keyboard = InlineKeyboardMarkup(row_width = 2)
    row_buttons = []
    if buttons != None:
        num_buttons = 0
        for button_text in buttons.keys():
            button = InlineKeyboardButton(text = button_text, callback_data = buttons[button_text])
            row_buttons.append(button)
            num_buttons += 1
            if num_buttons == 2:
                keyboard.add(*row_buttons)
                row_buttons = []
                num_buttons = 0
        if num_buttons > 0:
            keyboard.add(*row_buttons)
    if back != None:
        btn_return = InlineKeyboardButton(text = 'Назад', callback_data = f'return_{back}')
        keyboard.add(btn_return)
    return keyboard

def open_menu(name = None, call = None): # открытие меню в чате из файла
    # данные меню
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    # получение данных для меню
    if os.path.exists(path):
        data = open_data_menu(path)        
        text = None if isinstance(data['text'], str) and data['text'] == 'None' else data['text']
        buttons = None if data['buttons'] == 'None' else data['buttons']
        back = None if isinstance(data['back'], str) and data['back'] == 'None' else data['back']
        type_menu = None if isinstance(data['type_menu'], str) and data['type_menu'] == 'None' else data['type_menu']
        command = None if isinstance(data['command'], str) and data['command'] == 'None' else data['command']
    
        # работа с клавиатурами
        if buttons != None and buttons:
            buttons = eval(buttons)
            if 'menu_lists' in buttons:
                files = os.listdir(menu_user_path)
                new_buttons = {}
                for filename in files:
                    file_key = filename.split('.')[0]
                    new_buttons[file_key] = buttons['menu_lists']
                buttons = new_buttons
    
        keyboard = create_keyboard(buttons, back)
        try:
            if name == 'main' and id_admin == (call.chat.id):
                keyboard.add(InlineKeyboardButton(text = 'Администратор', callback_data = 'admin_admin'))
        except:
            if name == 'main' and id_admin == (call.message.chat.id):
                keyboard.add(InlineKeyboardButton(text = 'Администратор', callback_data = 'admin_admin'))
    
        # работа с типом меню
        if type_menu == 'insert_text':
            print(f'Ожидание ввода')
            x = f'command_{command}'
            bot.register_next_step_handler(call.message, globals()[x], call)
    
        # изменение сообщения
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup = keyboard)
        except AttributeError as e: # этот код должен срабатывать, если в чате вообще нет сообщений
            print(f'Ошибка в отправке меню: {e}')
            bot.send_message(call.chat.id, text, reply_markup = keyboard)
            bot.delete_message(chat_id=call.chat.id, message_id=call.message_id)
    
        try:
            if (call.text) == '/start': # удаление старого меню
                bot.delete_message(chat_id=call.chat.id, message_id=call.message_id - 1)
        except AttributeError:
            if (call.message.text) == '/start': # удаление старого меню
                bot.delete_message(chat_id=call.chat.id, message_id=call.message_id - 1)
        except:
            pass
            
    else:
        print(f"Меню {name} не найдено!")

def delete_menu(name, call):
    os.remove(f'{menu_user_path}/{name}.txt')
    print(f'Меню {name}.txt удалено!')

def command_create_menu(user_call, call):
    bot.delete_message(chat_id=user_call.chat.id, message_id=user_call.message_id)
    name = user_call.text
    create_menu(name)
    open_menu('settings-menu', call)

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

    if (call.data).split('_')[0] == 'return':
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        open_menu(name = (call.data).split('_')[1], call = call)

    if (call.data).split('_')[0] == 'admin':
        open_menu(name = (call.data).split('_')[1], call = call)
    else:
        print(call.data)

    

main_check()
print("Бот запущен...")

try:
    bot.polling()
except Exception as e:
    with open(error_path, 'w+', encoding='utf-8') as f:
        f.write(str(e) + "\n")
        goodbuy