from aiogram.dispatcher.filters.state import StatesGroup, State


# машина состояний для функции определения погоды
class CityState(StatesGroup):
    city_name = State()


# машина состояний для функции конвертации валюты
class ExchangeState(StatesGroup):
    input_value = State()
    output_value = State()
    amount = State()


# машина состояний для функции создания опроса
class PollState(StatesGroup):
    chat_id = State()
    question = State()
    options = State()
