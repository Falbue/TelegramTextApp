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