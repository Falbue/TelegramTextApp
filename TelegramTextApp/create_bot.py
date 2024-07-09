import sys
import os
import sqlite3
import shutil

object_menu = {'Текст':'text', 'Кнопки':'buttons', 'Возврат':'back', 'Тип':'type', 'Команда':'command'}
buttons_edit_menu = {key: f'admin_rename-object-{value}_[file-name]' for key, value in object_menu.items()}

dev_menu = [
    {"name": "admin", "text": 'Панель администратора', 'buttons': {'Настройка меню': 'admin_settings-menu', 'Управление командами': 'admin_control-command'}, 'back': 'main'},
    {"name": "settings-menu", "text": 'Найстройки меню', 'buttons': {'Редактировать': 'admin_list-edit-menu', '+ Создать': 'admin_create-menu', '× Удалить ': 'admin_list-delete-menu'}, 'back': 'admin'},
    {"name": "list-edit-menu", "text": 'Выберите меню, которое хотите отредактировать', 'buttons': {'[menu_lists]': 'admin_edit-menu'}, 'back': 'settings-menu'},
    {"name": "create-menu", "text": 'Введите название меню/n/nНазвание меню не должно содержать  *<_* !', 'back': 'settings-menu', 'type_menu': 'insertion', 'command': 'create_menu'},
    {"name": "list-delete-menu", "text": 'Выберите меню для удаления', 'buttons': {'[menu_lists]': 'admin_delete-menu'}, 'back': 'settings-menu'},
    {"name": "edit-menu", "text": '*Выбранное меню:* [file-name]/n/n[file-data]/n/nВыберите, что нужно изменить:', 'buttons': buttons_edit_menu, 'back': 'list-edit-menu'},
    {"name": "rename-object", "text": '*Введите:* [object-menu]', 'back': 'edit-menu_[file-name]', 'type_menu': 'insertion', 'command': 'rename_menu'},
    {"name": "control-command", "text": 'Выберите, нужное действие', 'buttons':{'Список команд': 'admin_list-commands', 'Добавить команду': 'admin_add-command', 'Удалить команду': 'admin_list-delete-command'}, 'back': 'admin'},
    {"name": "add-command", "text": 'Отправьте текст либо загрузите python файл', 'back': 'control-command', 'type_menu': 'insertion', 'command': 'create_command'},
    {"name": "list-delete-command", "text": 'Выберите, какую команду нужно удалить', 'buttons': {'[command_lists]': 'admin_delete-command'}, 'back': 'control-command'},
    {"name": "list-commands", "text": 'Все добавленные команды', 'buttons': {'[command_lists]': 'admin_open-command'},  'back': 'control-command'},
    {"name": "open-command", "text": '*Название: *[file-name]/n[file-code]', 'buttons':{'Переименовать':'admin_rename-command_[command-name]','Изменить код': 'admin_edit-command_[command-name]'}, 'back': 'list-commands'},
    {"name": "edit-command", "text": 'Отправьте текст либо загрузите python файл', 'type_menu': 'insertion', 'command': 'update_command', 'back': 'open-command_[file-name]'},
    {"name": "rename-command", "text": 'Введите новое название команды', 'type_menu': 'insertion', 'command': 'rename_command', 'back': 'list-commands'},
]

def create():
    if len(sys.argv) != 4:
        print("Usage: TTA <NAME> <API> <ID_ADMIN>")
        sys.exit(1)
    
    NAME = sys.argv[1]
    NAME_dir = f'Falbue/TelegramTextApp/{NAME}'
    API = sys.argv[2]
    ID = int(sys.argv[3])

    main_check(NAME_dir)
    create_config(API, ID, NAME, NAME_dir)
    print(f"{NAME} создан!")

def main_check(folder_path): # основные проверки
    script_dir = os.path.dirname(os.path.abspath(__file__))
    global menu_user_path, menu_dev_path
    db_name = "database.db"
    db_path = os.path.join(folder_path, db_name)
    texts_path = f"{folder_path}/texts"
    menu_user_path = f'{folder_path}/user_menu'
    menu_dev_path = f'{folder_path}/telegram_text_apps_menu'
    error_path = f'{texts_path}/error_log.txt'
    command_path = f'{folder_path}/command'

    if not os.path.exists(f"{folder_path}"):
        os.makedirs(f"{folder_path}")
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
    if not os.path.exists(command_path):
        os.makedirs(command_path)
        print("Папка с командами создана")   
    if not os.path.exists(error_path):
        with open(error_path, 'w'): 
            pass
        print("Файл с логами ошибок создан")
    if not os.path.exists(f'{menu_user_path}/main.txt'):
        create_menu('main', 'Главное меню') # создание главного меню
        print('Главное меню создано!')
    if not os.path.exists(db_path):
        conn = sqlite3.connect(f"{folder_path}/database.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                user_id INTEGER,
                time_registration INTEGER,
                id_message INTEGER);
            ''')
        conn.close()
        print("База данных создана")

    source = f'{script_dir}/bot.py'
    destination = f'{folder_path}'
    shutil.copy(source, destination)

    create_dev_menu()

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

def create_menu(name=None, text='Измените текст!', buttons=None, back='main', type_menu=None, command=None): # создание меню
    name = name.replace('_', '-')
    print(f'Создано меню: {name}')
    path = f'{menu_user_path}/{name}.txt'
    if name in [menu_item['name'] for menu_item in dev_menu]: 
        path = f'{menu_dev_path}/{name}.txt'
    if name == 'main':
        back = None

    with open(path, 'w+', encoding='utf-8') as file:
        file.write(f'text: {text}\nbuttons: {buttons}\nback: {back}\ntype: {type_menu}\ncommand: {command}')

def create_config(API, ID, NAME, NAME_dir):
     with open(f'{NAME_dir}/config.py', 'w+', encoding='utf-8') as file:
        file.write(f'API = "{API}"\nID = {ID}\nNAME = "{NAME}"')
    print("Конфиг создан!")

create()