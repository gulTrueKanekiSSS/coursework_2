import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
import psycopg2

load_dotenv()
database = os.getenv('DATABASE')
token = os.getenv('TG_TOKEN')
host = os.getenv('HOST')
user = os.getenv('USER_DB')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')


bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

connection = psycopg2.connect(
                            database=database,
                            host=host,
                            user=user,
                            password=password,
                            port=port
                            )