'''Файл конфигурации бота и базы данных'''

import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
import psycopg2

load_dotenv()
database = os.getenv('DATABASE')
token = os.getenv('TG_TOKEN')
host = os.getenv('HOST')
user = os.getenv('USER_DB')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

connection = psycopg2.connect(
                            database=database,
                            host=host,
                            user=user,
                            password=password,
                            port=port
                            )

#P.S. используйте свои значения для конфигураций если хотите запустить программу(database - Название бд
#                                                                               token - токен вашего бота
#                                                                               host - host database
#                                                                               user - пользователь бд
#                                                                               password - пароль от вашей бд
#                                                                               port - порт бд(по умолчанию - 5432)
#                                                                                )