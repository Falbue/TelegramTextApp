# bot_api = ""
bot_api = '' # бот для тестов
folder = 'data'
# folder = '/data'


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
    if os.path.exists(db_path):
        print("База данных существует")
    else:
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

def now_time():
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M")
    current_date = now_moscow.strftime("%m.%d.%Y")
    date = f"{current_date} {current_time}"
    return date


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
    x = back.split('_')[0]
    if x == 'return':
        btn_return = InlineKeyboardButton(text = 'Назад', callback_data = back)
        keyboard.add(btn_return)
    return keyboard

def create_menu(name, text, buttons, back, call):
    keyboard = create_keyboard(buttons, back)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup = keyboard)



def menu_main(call):
    text = "Главное меню"
    buttons = ["Первая:", "Вторая:", "Третья", "sdfsdf"]
    create_menu("main", text, buttons, 'none', call)

def menu_one(call):
    text = "Проверка"
    buttons = ['Проверочная']
    create_menu("test", text, buttons, 'return_main', call)



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
    bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup = keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'start': menu_main(call)
    if call.data == 'Первая_data': menu_one(call)

    if (call.data).split('_')[0] == 'return':
        menu = (call.data).split('_')[1]
        menu_callback = f"menu_{menu}"
        globals()[menu_callback](call)



main_check()
print("Бот запущен...")
bot.polling()