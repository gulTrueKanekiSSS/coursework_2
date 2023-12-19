from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_mods = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard_mods.add(KeyboardButton('GPT'))
keyboard_mods.add(KeyboardButton('Работодатели'))