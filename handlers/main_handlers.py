import json
from pprint import pprint
import random

import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import open_weather_token, exchange_token
from create_bot import bot, dp
from keyboards.main_keyboard import menu_kb
from states.state import CityState, ExchangeState, PollState


# Команда старт, вызывает основное меню
async def start_point(message: types.Message):
    await message.answer(f'Приветствую вас, {message.from_user.username}!\nС чего хотите начать?', reply_markup=menu_kb)


# Функция по определению погоды
async def weather(call: CallbackQuery):
    await call.answer('В каком городе хотите узнать погоду?\n(напишите название на английском)')
    # запуск машины состояний, захват названия города
    await CityState.city_name.set()


# Функция в которой мы сохраняем город и вызываем функцию по запрашиванию погоды
async def weather_output(message: types.Message, state: FSMContext):
    city_name = message.text
    await state.update_data(city_name=city_name)
    data = await state.get_data()
    city = data.get('city_name')
    # передаём функцию определения погоды в сообщение
    await message.answer(get_weather(city, open_weather_token), reply_markup=menu_kb)
    await state.finish()


# Функция определения погоды по полученным данным о городе
def get_weather(city, token):
    try:
        # get запрос с параметрами
        request = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token}&units=metric')
        data = request.json()
        city = data['name']
        temp = data['main']['temp']
        pprint(data)
        # возвращаем строку и передаем функцию как аргумент в функцию выше
        return f'Погода в городе: {city}.\nТемпература: {temp}'

    except Exception as er:
        print(f'ERROR: {er}')


# Функция конвертации валюты
async def exchange(call: CallbackQuery):
    await call.answer('Какую валюту хотите обменять?')
    # запрашиваем валюту для конвертации
    await ExchangeState.input_value.set()


# запрашиваем валюту в которую будем конвертировать
async def exchange_input(message: types.Message, state: FSMContext):
    input_value = message.text
    await state.update_data(input_value=input_value)
    await message.answer('На какую валюту хотите обменять?')
    await ExchangeState.output_value.set()


# запрашиваем кол-во валюты для конвертации
async def exchange_output(message: types.Message, state: FSMContext):
    output_value = message.text
    await state.update_data(output_value=output_value)
    await message.answer('Введите кол-во валюты для обмена')
    await ExchangeState.amount.set()


# конечная функция конвертации
async def exchange_results(message: types.Message, state: FSMContext):
    amount = message.text
    await state.update_data(amount=amount)
    data = await state.get_data()
    input_val = data['input_value']
    output_val = data['output_value']
    amount = data['amount']
    # передаём функцию, которая запрашивает данные, как аргумент в сообщение
    await message.answer(exchange_func(input_val, output_val, amount), reply_markup=menu_kb)
    await state.finish()


# функция с get запросом для конвертации валюты
def exchange_func(input_val, output_val, amount):
    try:
        headers = {
            'apikey': exchange_token
        }
        r = requests.get(
            f'https://api.apilayer.com/exchangerates_data/convert?&from={input_val}&to={output_val}&amount={amount}',
            headers=headers)
        data = r.json()
        result = data['result']
        # возвращаем строку и передаём функцию выше
        return f'Конвертация из {input_val} в {output_val} ровна {result}'

    except Exception as er:
        print(f'ERROR - {er}')


# функция для отправки рандомной картинки (можно подключить базу данных)
async def picture(message: types.Message):
    images = ['/Users/faithk/Documents/test_task_tg_bot/images/pic1.jpg',
              '/Users/faithk/Documents/test_task_tg_bot/images/pic2.jpg',
              '/Users/faithk/Documents/test_task_tg_bot/images/pic3.jpg',
              '/Users/faithk/Documents/test_task_tg_bot/images/pic4.jpg',
              '/Users/faithk/Documents/test_task_tg_bot/images/pic5.jpg',
              '/Users/faithk/Documents/test_task_tg_bot/images/pic6.jpg']
    img = random.choice(images)
    with open(img, 'rb') as img:
        await message.answer_photo(photo=img, reply_markup=menu_kb)


# начальная функция для опроса, запрашиваем chat_id
async def poll(message: types.Message):
    await message.answer('Начинаю создание опроса\nУкажите группу для отправки.')
    await PollState.chat_id.set()


# запрашиваем вопрос для опроса
async def poll_question(message: types.Message, state: FSMContext):
    chat_id = message.text
    await state.update_data(chat_id=chat_id)
    await message.answer('Теперь введите ваш вопрос.')
    await PollState.question.set()


# запрашиваем варианты ответов для опроса
async def poll_answers(message: types.Message, state: FSMContext):
    question = message.text
    await state.update_data(question=question)
    await message.answer('Добавить вариант ответа.')
    await PollState.options.set()


# конечная функция для опроса, разделяем ответы и формируем опрос
async def poll_result(message: types.Message, state: FSMContext):
    option = message.text.split(', ')
    option_json = json.dumps(option)
    await state.update_data(options=option_json)

    data = await state.get_data()
    chat_id = data['chat_id']
    question = data['question']
    options = data['options']

    await message.answer('Вы создали опрос', reply_markup=menu_kb)
    await bot.send_poll(chat_id, question, options)


# регистрация хендлеров
def register_handlers_main(dp: Dispatcher):
    dp.register_message_handler(start_point, commands=['start'])
    dp.register_message_handler(weather, commands=['Погода'])
    dp.register_message_handler(exchange, commands=['Валюта'])
    dp.register_message_handler(picture, commands=['Картинка'])
    dp.register_message_handler(poll, commands=['Опрос'])
    dp.register_message_handler(weather_output, state=CityState.city_name)
    dp.register_message_handler(exchange_input, state=ExchangeState.input_value)
    dp.register_message_handler(exchange_output, state=ExchangeState.output_value)
    dp.register_message_handler(exchange_results, state=ExchangeState.amount)
    dp.register_message_handler(poll_question, state=PollState.chat_id)
    dp.register_message_handler(poll_answers, state=PollState.question)
    dp.register_message_handler(poll_result, state=PollState.options)
