from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu_kb1 = KeyboardButton('/Погода')
menu_kb2 = KeyboardButton('/Валюта')
menu_kb3 = KeyboardButton('/Картинка')
menu_kb4 = KeyboardButton('/Опрос')
menu_kb.add(menu_kb1).add(menu_kb2).add(menu_kb3).add(menu_kb4)