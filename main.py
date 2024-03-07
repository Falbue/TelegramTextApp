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
