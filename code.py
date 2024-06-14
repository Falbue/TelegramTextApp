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

object_menu = {'Текст':'text', 'Кнопки':'buttons', 'Возврат':'back', 'Тип меню':'typemenu', 'Команда':'command'}
buttons_edit_menu = {key: f'admin_rename-object-{value}_[file-name]' for key, value in object_menu.items()}
print (buttons_edit_menu)

dev_menu = [
    {"name": "admin", "text": 'Панель администратора', 'buttons': {'Настройка меню': 'admin_settings-menu'}, 'back': 'main'},
    {"name": "settings-menu", "text": 'Найстройки меню', 'buttons': {'Редактировать': 'admin_list-edit-menu', 'Создать': 'admin_create-menu', 'Удалить': 'admin_delete-menu'}, 'back': 'admin'},
    {"name": "list-edit-menu", "text": 'Выберите меню, которое хотите отредактировать', 'buttons': {'[menu_lists]': 'admin_edit-menu'}, 'back': 'settings-menu'},
    {"name": "create-menu", "text": 'Введите название меню', 'back': 'settings-menu', 'type_menu': 'insert_text', 'command': 'create_menu'},
    {"name": "delete-menu", "text": 'Выберите меню для удаления', 'buttons': {'[menu_lists]': 'admin_delete'}, 'back': 'settings-menu'},
    {"name": "edit-menu", "text": '[file-name]/n/n[file-data]/n/nВыберите, что нужно изменить', 'buttons': buttons_edit_menu, 'back': 'list-edit-menu'},
    {"name": "rename-object", "text": 'Введите: [object-menu]', 'back': 'edit-menu_[file-name]', 'type_menu': 'insert_text', 'command': 'rename_menu'},
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
    if not os.path.exists(f'{menu_user_path}/main.txt'):
        create_menu('main', 'Главное меню') # создание главного меню
        print('Главное меню создано!')
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

def markdown_text(text, call): # mardown разметка 
    if text != None and '[' in text:
        filename = call.data.split('_')[2]
        path = f'{menu_user_path}/{filename}.txt'
        if filename in [menu_item['name'] for menu_item in dev_menu]: path = f'{menu_dev_path}/{filename}.txt'
        with open(path, encoding='utf-8') as file:
            data = file.read()
        try:
            object_m = (call.data).split('-')[2].split('_')[0]
            for key, value in object_menu.items():
                if object_m in value:
                    object_m = key
                    text = text.replace('[object-menu]', object_m)
        except:pass
        text = text.replace('[file-name]', filename)
        text = text.replace('[file-data]', data)

    text = text.replace('/n', '\n')

    return(text)

def create_menu(name=None, text='Измените текст!', buttons=None, back='main', type_menu=None, command=None): # создание меню
    print(f'Создано меню: {name}')
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    if name == 'main':
        back = None

    with open(path, 'w+', encoding='utf-8') as file:
        file.write(f'text: {text}\nbuttons: {buttons}\nback: {back}\ntype-menu: {type_menu}\ncommand: {command}')

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

def open_data_menu(name): # получение всех данных из файла
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    if os.path.exists(path):
        with open(path, encoding='utf-8') as file:
            file_data = file.read()
            data = {}
            for line in file_data.splitlines():
                key, value = line.split(': ', 1)
                data[key.strip()] = value.strip()
    else:data = None
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
    # получение данных для меню
    data = open_data_menu(name)        
    if data != None:
        text = None if isinstance(data['text'], str) and data['text'] == 'None' else data['text']
        buttons = None if data['buttons'] == 'None' else data['buttons']
        back = None if isinstance(data['back'], str) and data['back'] == 'None' else data['back']
        type_menu = None if isinstance(data['type-menu'], str) and data['type-menu'] == 'None' else data['type-menu']
        command = None if isinstance(data['command'], str) and data['command'] == 'None' else data['command']

        # работа с текстом
        text = markdown_text(text, call)

        # работа с клавиатурами
        if buttons is not None and buttons:
            buttons = eval(buttons)
            if '[menu_lists]' in buttons:
                files = os.listdir(menu_user_path)
                new_buttons = {}
                for filename in files:
                    file_key = filename.split('.')[0]
                    if buttons['[menu_lists]'].split('_')[1] != 'delete':
                        main = buttons['[menu_lists]'] + '_' + 'main'
                        if 'main' not in new_buttons:
                            new_buttons['main'] = main
                    new_buttons[file_key] = buttons['[menu_lists]'] + '_' + file_key
                buttons = new_buttons

            new_buttons = {}
            for key, value in buttons.items():
                if '[file-name]' in value:
                    new_value = markdown_text(value, call)
                    new_buttons[key] = new_value
                else:
                    new_buttons[key] = value
            buttons = new_buttons

        if back != None:
            back = markdown_text(back, call)
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
            bot.send_message(call.chat.id, text, reply_markup = keyboard)
            bot.delete_message(chat_id=call.chat.id, message_id=call.message_id)
        
    else:
        print(f"Меню {name} не найдено!")

def delete_menu(name, call): # удаление меню
    os.remove(f'{menu_user_path}/{name}.txt')
    print(f'Меню {name}.txt удалено!')
    notification('Меню удалено!', 'delete-menu', call = call)

def notification(text=None, back=None, all_users=None, call=None): # вставка меню (без создания)
    buttons={}
    keyboard = create_keyboard(buttons, back)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup = keyboard)

def command_create_menu(user_call, call):
    bot.delete_message(chat_id=user_call.chat.id, message_id=user_call.message_id)
    name = user_call.text
    create_menu(name)
    notification('Меню создано!', 'settings-menu', call = call)

def command_rename_menu(user_call, call):
    bot.delete_message(chat_id=user_call.chat.id, message_id=user_call.message_id)
    rename = (call.data).split('-')[2]
    rename = rename.split('_')[0]
    name = (call.data).split('_')[2]

    data = open_data_menu(name)
    data[rename] = user_call.text
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    with open(path, 'w', encoding='utf-8') as file:
        for key, value in data.items():
            file.write(f"{key}: {value}\n")

    open_menu('edit-menu', call = call)

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
        c.execute(f"UPDATE users SET id_message = {(message_id)} WHERE user_id = {message.chat.id}")
        print('Пользователь' ,message.chat.id,'уже существует в базе')
        conn.commit()
        pass
    conn.close()

    open_menu('main', message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.data)
    if (call.data).split('_')[0] == 'return':
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        open_menu(name = (call.data).split('_')[1], call = call)
    elif str((call.data)).count('_') <= 1:
        if (call.data).split('_')[0] == 'admin':
            open_menu(name = (call.data).split('_')[1], call = call)
        if (call.data).split('_')[0] == 'user':
            open_menu(name = (call.data).split('_')[1], call = call)


    elif str((call.data)).count('_') <= 2:
        if (call.data).split('_')[0] == 'admin' and (call.data).split('_')[1] == 'delete':
            delete_menu((call.data).split('_')[2], call)
        elif (call.data).split('_')[0] == 'admin' and (call.data).split('_')[1] == 'edit-menu':
            print((call.data).split('-')[1])
            open_menu((call.data).split('_')[1], call = call)
        elif (call.data).split('_')[0] == 'admin' and ((call.data).split('_')[1].split('-')[0]) == 'rename':
            rename_object = (call.data).split('-')[2].split('_')[0]
            for y, x in object_menu.items():
                if x == rename_object:
                    open_menu('rename-object', call = call)

    else:
        print(f'Вызов не найден: {call.data}')
        print(str((call.data)).count('_'))

    
main_check()
print("Бот запущен...")

try:
    bot.polling()
except Exception as e:
    with open(error_path, 'w+', encoding='utf-8') as f:
        f.write(str(e) + "\n")
        goodbuy