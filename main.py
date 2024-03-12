bot_api = ''
folder = 'data'
# folder = '/data'
id_admin =
# -----------------------------------------------------------


import os
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
import re
from datetime import datetime
import pytz
from flask import Flask
import sys
sys.path.append(folder)
import threading
bot = telebot.TeleBot(bot_api)


# переменные
folder_path = f"{folder}"
texts_path = f"{folder}/texts"
error_path = f'{texts_path}/error_log.txt'
db_name = "database.db"
db_path = os.path.join(folder_path, db_name)


# основные функции
def main_check():
    if not os.path.exists(f"{folder}"):
        os.makedirs(f"{folder}")
        print("Папка библиотеки создана")
    if not os.path.exists(texts_path):
        os.makedirs(texts_path)
        print("Папка текстов создана")    
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
                course INTEGER,
                groupe INTEGER,
                time_registration INTEGER,
                id_message INTEGER);
            ''')
        conn.close()
        print("База данных создана")

def now_time():
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M")
    current_date = now_moscow.strftime("%m.%d.%Y")
    date = f"{current_date} {current_time}"
    return date


def insertion(text = None, buttons = None, menu = None):
    with sqlite3.connect(f'{folder}/database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            call = [row[0], row[4]]
            try:
                if menu != None:
                    globals()[menu](call)
                else:
                    create_menu(name = 'insertion', text = text, call = call, buttons = buttons)
            except Exception as e:
                print(f'Ошибка во вставке: {e}')
                bot.edit_message_text(chat_id=call[0], message_id=call[1], text='Возникла ошибка. Перезапуск...', reply_markup='')


def create_keyboard(buttons, back):
    keyboard = InlineKeyboardMarkup(row_width = 2)
    row_buttons = []
    num_buttons = 0
    for i in range(len(buttons)):
        if buttons[i].endswith(':'):
            button_text = (buttons[i]).replace(':', '')
            num_buttons = 1
        else:
            button_text = (buttons[i])
        button_callback_data = f"{button_text}_data"
        button = InlineKeyboardButton(text = button_text, callback_data = button_callback_data)
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

def create_menu(name = None, text = None, call = None, buttons = None, back = None):
    if buttons == None and back == None:
        keyboard = ''
    elif buttons == None or back != None:
       keyboard = create_keyboard('', back)
    else: 
        keyboard = create_keyboard(buttons, back)
        for i in range(len(buttons)):
            create_menu(
                name = buttons[i],
                text = 'Доавьте текст',
                buttons = buttons,
                back = name)

    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup = keyboard)
    except AttributeError:
        bot.edit_message_text(chat_id = call[0], message_id = call[1], text = text, reply_markup = keyboard)


# создание менюшек
def menu_main(call):
    text = "Главное меню"
    buttons = ["Первая", "Вторая"]
    try:
        if call[0] == id_admin:
            buttons.append('Администратор')
    except:
        if call.message.chat.id == id_admin:
           buttons.append('Администратор') 
    create_menu(
        name = 'main',
        text = text,
        call = call,
        buttons = buttons
        )


@bot.message_handler(commands=['start'])
def start(message):
    message_id = message.id
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (message.chat.id,))
    result = c.fetchone()
    if result is None:
        registration = now_time()
        c.execute("INSERT INTO users (user_id, course, groupe, time_registration, id_message) VALUES (?, ?, ?, ?, ?)",
                  (message.chat.id, 0, 0, registration, message_id+1))
        conn.commit()
        print('Зарегистрирован новый пользователь', message.chat.id)
    else:
        c.execute(f"UPDATE users SET id_message = {(message_id+1)} WHERE user_id = {message.chat.id}")
        print('Пользователь' ,message.chat.id,'уже существует в базе')
        conn.commit()
        pass
    conn.close()

    keyboard = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text = "Запустить", callback_data = 'start')
    keyboard.add(btn)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup = keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'start': menu_main(call)
    if call.data == 'Запустить_data': menu_main(call)


    if (call.data).split('_')[0] == 'return':
        menu = (call.data).split('_')[1]
        menu_callback = f"menu_{menu}"
        globals()[menu_callback](call)


    if call.data == 'del_message': bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


    else: 
        x = call.data
        print(f"call: {call.data}")




def send_start_message():
    keyboard_start_message = InlineKeyboardMarkup()
    keyboard_start_message.add(InlineKeyboardButton(text='Прочитано', callback_data='del_message'))

    insertion('Обновление...')
    buttons = ['Запустить']
    insertion(menu = 'menu_main')
    
    try:
        with open(error_path, 'r+', encoding='utf-8') as f:
            text_error = f.read()
            if not text_error.strip():
                return 
    except Exception as e:
        text_error = f'Ошибка в поиске лога: {e}'
        print(text_error)
    else:
        with open(error_path, 'w+', encoding='utf-8') as f:
            print("Файл с логом очищен")

    bot.send_message(chat_id=id_admin, text=f"Бот перезапущен\n{now_time()}\nОшибка: {text_error}", reply_markup=keyboard_start_message)


main_check()
send_start_message()
print("Бот запущен...")
try:
    bot.polling()
except Exception as e:
    with open(error_path, 'w+', encoding='utf-8') as f:
        f.write(str(e) + "\n")
        insertion("Возникли технические проблемы. В скором времени всё заработает...")
        goodbuy