import os
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
from datetime import datetime
import pytz
import config
import sys

bot_dir = os.path.dirname(os.path.abspath(__file__))

bot_api = config.API
id_admin = config.ID
name_bot = config.NAME

bot = telebot.TeleBot(bot_api)

# пути
folder_path = f"{bot_dir}"
db_name = "database.db"
db_path = os.path.join(folder_path, db_name)
texts_path = os.path.join(folder_path, 'texts')
menu_user_path = os.path.join(folder_path, 'user_menu')
menu_dev_path = os.path.join(folder_path, 'telegram_text_apps_menu')
command_path = os.path.join(folder_path, 'command')
error_path = os.path.join(texts_path, 'error_log.txt')

object_menu = {'Текст':'text', 'Кнопки':'buttons', 'Возврат':'back', 'Тип':'type', 'Команда':'command'}

files = os.listdir(menu_dev_path)
dev_menu = [os.path.splitext(file)[0] for file in files]


# основные функции
def now_time(): # получение текущего времени
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M")
    current_date = now_moscow.strftime("%m.%d.%Y")
    date = f"{current_date} {current_time}"
    return date

def escape_markdown(text): # экранирование любых символов текста
    special_characters = r'_*[]()~>#+-=|{}.!`'
    escaped_text = ''
    for char in text:
        if char in special_characters:
            escaped_text += '//' + char
        else:
            escaped_text += char
    return escaped_text

def tg_markdown(text): # экранирование только для телеграма
    special_characters = r'[]()>#+-=|{}.!'
    escaped_text = ''
    for char in text:
        if char in special_characters:
            escaped_text += '//' + char
        else:
            escaped_text += char
    return escaped_text

def square_rename(text, call): # замена квадратных скобок
    if '[file-name]' in text:
        text = text.replace('[file-name]', call.data.split('_')[2])

    if '[file-code]' in text:
        filename = call.data.split('_')[2]
        path = f'{command_path}/{filename}.py'
        with open(path, encoding='utf-8') as file:
            code = file.read()
        text = text.replace('[file-code]', f'```\n{code}\n```')

    if '[object-menu]' in text:
        object_m = (call.data).split('-')[2].split('_')[0]
        for key, value in object_menu.items():
            if object_m in value:
                object_m = key
                text = text.replace('[object-menu]', object_m)

    if '[file-data]' in text:
        filename = call.data.split('_')[2]
        path = f'{menu_user_path}/{filename}.txt'
        if filename in [menu_item for menu_item in dev_menu]: path = f'{menu_dev_path}/{filename}.txt'
        with open(path, encoding='utf-8') as file:
            data = file.read()
            data = escape_markdown(data)
        text = text.replace('[file-data]', data)

    if '[command-name]' in text:
        text = text.replace('[command-name]', call.data.split('_')[2])

    return text

def markdown_text(text, call): # mardown разметка
    text = text.replace('/n', '\n')
    text = square_rename(text, call)
    text = tg_markdown(text)
    text = text.replace('////', '//')
    text = text.replace('<', '//')
    text = text.replace('//', '\\')
    text = text.replace('/n', f' _~enter~_ ')
    return(text)

def create_menu(name=None, text='Измените текст!', buttons=None, back='main', type_menu=None, command=None): # создание меню
    name = name.replace('_', '-')
    print(f'Создано меню: {name}')
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    if name == 'main':
        back = None

    with open(path, 'w+', encoding='utf-8') as file:
        file.write(f'text: {text}\nbuttons: {buttons}\nback: {back}\ntype: {type_menu}\ncommand: {command}')

def open_data_menu(name): # получение всех данных из файла
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item for menu_item in dev_menu]: 
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
        btn_return = InlineKeyboardButton(text = '< Назад', callback_data = f'return_{back}')
        keyboard.add(btn_return)
    return keyboard

def update_buttons(buttons, path, key, exclude_main=False):
    # замена квадратных скобок
    files = os.listdir(path)
    new_buttons = {}
    for filename in files:
        if exclude_main and filename == 'main.txt': 
            continue
        file_key = filename.split('.')[0]
        new_buttons[file_key] = buttons[key] + '_' + file_key
    return new_buttons

def open_menu(name = None, call = None): # открытие меню в чате из файла
    # получение данных для меню
    data = open_data_menu(name)        
    if data != None:
        text = None if isinstance(data['text'], str) and data['text'] == 'None' else data['text']
        buttons = None if data['buttons'] == 'None' else data['buttons']
        back = None if isinstance(data['back'], str) and data['back'] == 'None' else data['back']
        type_menu = None if isinstance(data['type'], str) and data['type'] == 'None' else data['type']
        command = None if isinstance(data['command'], str) and data['command'] == 'None' else data['command']

        # работа с текстом
        text = markdown_text(text, call)

        # работа с клавиатурами
        if buttons is not None and buttons:
            buttons = eval(buttons)
            if '[menu_lists]' in buttons:
                exclude_main = buttons['[menu_lists]'].split('_')[1] == 'delete-menu'
                buttons = update_buttons(buttons, menu_user_path, '[menu_lists]', exclude_main)
            
            if '[command_lists]' in buttons:
                buttons = update_buttons(buttons, command_path, '[command_lists]')

            new_buttons = {}
            for key, value in buttons.items():
                if '[file-name]' in value:
                    new_value = square_rename(value, call)
                    new_buttons[key] = new_value
                elif '[command-name]' in value:
                    new_value = square_rename(value, call)
                    print(new_value)
                    new_buttons[key] = new_value
                else:
                    new_buttons[key] = value
            buttons = new_buttons

        # работа с возвратом
        if back != None:
            back = square_rename(back, call)

        keyboard = create_keyboard(buttons, back)
        try:
            if name == 'main' and id_admin == (call.chat.id):
                keyboard.add(InlineKeyboardButton(text = 'Администратор', callback_data = 'admin_admin'))
        except:
            if name == 'main' and id_admin == (call.message.chat.id):
                keyboard.add(InlineKeyboardButton(text = 'Администратор', callback_data = 'admin_admin'))

        # изменение сообщения
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup = keyboard, parse_mode = 'MarkdownV2')
        except AttributeError as e: # этот код должен срабатывать, если в чате вообще нет сообщений
            bot.send_message(call.chat.id, text, reply_markup = keyboard, parse_mode = 'MarkdownV2')
            bot.delete_message(chat_id=call.chat.id, message_id=call.message_id) 

        # работа с типом меню
        if type_menu == 'insertion':
            print(f'Ожидание ввода')
            if command in ['create_menu','rename_menu','create_command', 'rename_command', 'update_command']:
                bot.register_next_step_handler(call.message, globals()[f'command_{command}'], call)
            else:
                bot.register_next_step_handler(call.message, open_command, call, command)
        if type_menu == 'click':
            open_command('none', call, command)
        
    else:
        print(f"Меню {name} не найдено!")

def delete_menu(name, call): # удаление меню
    os.remove(f'{menu_user_path}/{name}.txt')
    print(f'Меню {name}.txt удалено!')
    notification('Меню удалено!', 'list-delete-menu', call = call)
    bot.answer_callback_query(callback_query_id=call.id, text="Меню удалено!")

def delete_command(name, call): # удаление меню
    name = name.replace('admin_delete-command_', '')
    os.remove(f'{command_path}/{name}.py')
    print(f'Команда {name}.py удалена!')
    notification('Команда удалена!', 'list-delete-command', call = call)
    bot.answer_callback_query(callback_query_id=call.id, text="Команда удалена!")

def notification(text=None, back=None, all_users=None, call=None): # вставка меню (без создания)
    buttons={}
    keyboard = create_keyboard(buttons, back)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = text, reply_markup = keyboard, parse_mode = 'HTML')

def command_create_menu(user_call, call): # команда создания меню
    bot.delete_message(chat_id=user_call.chat.id, message_id=user_call.message_id)
    name = user_call.text
    create_menu(name)
    bot.answer_callback_query(callback_query_id=call.id, text="Меню успешно создано!")
    notification('Меню создано!', 'settings-menu', call = call)

def command_rename_menu(user_call, call): # команда изменения меню
    bot.delete_message(chat_id=user_call.chat.id, message_id=user_call.message_id)
    rename = (call.data).split('-')[2]
    rename = rename.split('_')[0]
    name = (call.data).split('_')[2]
    text = (user_call.text).replace('\n', '/n')
    if text == '':
        text = None

    if rename == 'buttons':
        buttons = {}
        if text.count(',') > 0:
            elements = text.split(',')
            for element in elements:
                button_text, button_call = element.split(':')
                button_call = button_call.replace(' ', '')
                buttons[button_text] = f'user_{button_call}'
        else:
            button_text, button_call = text.split(':')
            button_call = button_call.replace(' ', '')
            buttons[button_text] = f'user_{button_call}'
        text = str(buttons)

    data = open_data_menu(name)
    data[rename] = text
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    with open(path, 'w', encoding='utf-8') as file:
        for key, value in data.items():
            file.write(f"{key}: {value}\n")

    open_menu('edit-menu', call = call)

def command_create_command(message, call): # команда создания команд
    if message.document: # Обработка документа
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        filename = message.document.file_name
        filename = filename.replace('_', '-')

        with open(f'{command_path}/{filename}', 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.answer_callback_query(callback_query_id=call.id, text="Команда добавлена!")
        notification('Команда добавлена!', 'control-command', call=call)

    elif message.text:
        text_content = message.text
        existing_files = os.listdir(command_path)
        max_number = 0
        for file in existing_files:
            if file.startswith('command_') and file.endswith('.py'):
                try:
                    number = int(file[len('command_'):-len('.py')])
                    if number > max_number:
                        max_number = number
                except ValueError:
                    continue

        new_number = max_number + 1
        file_name = f'{command_path}/command-{new_number}.py'

        with open(file_name, 'w', encoding='utf-8') as text_file:
            text_file.write(text_content)

        bot.answer_callback_query(callback_query_id=call.id, text="Команда добавлена!")
        notification('Команда успешно конвертирована и добавлена!', 'control-command', call=call)

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

def command_update_command(message, call): # команда изменения команды
    if message.document: # Обработка документа
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        filename = message.document.file_name
        filename = filename.replace('_', '-')

        with open(f'{command_path}/{filename}', 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.answer_callback_query(callback_query_id=call.id, text="Команда изменена!")
        notification('Команда изменена!', 'control-command', call=call)

    elif message.text:
        name = (call.data).split('_')[2]
        text_content = message.text
        existing_files = os.listdir(command_path)
        file_name = f'{command_path}/{name}.py'

        with open(file_name, 'w', encoding='utf-8') as text_file:
            text_file.write(text_content)

        bot.answer_callback_query(callback_query_id=call.id, text="Команда обновлена!")
        notification('Команда успешно конвертирована и обновлена!', 'control-command', call=call)

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

def command_rename_command(message, call): # команда переименования файла команды
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    old_name = (call.data).split('_')[2]
    new_name = message.text
    os.rename(f"{command_path}/{old_name}.py", f"{command_path}/{new_name}.py")

def open_command(message, call, command):
    filename = f'{command_path}/{command}.py'
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
        local_vars = {
            'message': message,
            'call': call,
            'bot': bot  # Если `bot` тоже используется в файле
        }
        exec(code, globals(), local_vars)
        print(f"Код из {filename} успешно выполнен.")
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
    except Exception as e:
        print(f"Ошибка при выполнении кода из файла {filename}: {e}")

def db_add_user(message): # фунция добавления пользователя в базу приложения
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

@bot.message_handler(commands=['start'])
def start(message): # обработка команды start
    db_add_user(message)
    open_menu('main', message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if (call.data).split('_')[0] == 'admin' and (call.data).split('_')[1] == 'delete-menu':
        delete_menu((call.data).split('_')[2], call)
    elif (call.data).split('_')[0] == 'admin' and (call.data).split('_')[1] == 'delete-command':
        delete_command(call.data, call)

    elif (call.data).split('_')[0] == 'admin' and ((call.data).split('_')[1].split('-')[0]) == 'rename' and ((call.data).split('_')[1].split('-')[1]) == 'object':
        open_menu('rename-object', call = call)

    elif (call.data).split('_')[0] == 'return':
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        open_menu(name = (call.data).split('_')[1], call = call)

    else:
        open_menu((call.data).split('_')[1], call = call)

print("Бот запущен...")

try:
    bot.polling(non_stop = True)
except Exception as e:
    with open(error_path, 'w+', encoding='utf-8') as f:
        f.write(str(e) + "\n")
        goodbuy