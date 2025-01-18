import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from data_providers.weather_api import WeatherApi
from database import DatabaseAPI

weather_router = Router()


class WeatherState(StatesGroup):
    any_city_state = State()


@weather_router.message(Command("weather"))
async def weather(message: Message) -> None:
    await weather_handler(message)


@weather_router.message(lambda message: message.text == ButtonText.WEATHER)
async def weather_handler(message: Message) -> None:
    keyboard = KeyboardBuilder.weather_reply_keyboard()
    await message.answer(AnswerText.WEATHER_ACTION, reply_markup=keyboard)


@weather_router.message(lambda message: message.text == ButtonText.WEATHER_IN_YOUR_CITY)
async def your_city(message: Message):
    user_city = await DatabaseAPI.get_user_city(message.from_user.id)
    weather_your_city = asyncio.create_task(
        WeatherApi.get_weather_with_coor(
            lat=user_city.latitude,
            lon=user_city.longitude,
        )
    )
    result = await weather_your_city
    parsed_result = WeatherApi.parse_response(result, user_city.name)
    await message.reply(
        AnswerText.WEATHER_IN_YOUR_CITY.format(result=parsed_result),
        reply_markup=KeyboardBuilder.main_reply_keyboard(),
    )


@weather_router.message(lambda message: message.text == ButtonText.WEATHER_IN_ANY_CITY)
async def any_city(message: Message, state: FSMContext) -> None:
    await state.set_state(WeatherState.any_city_state)
    await message.answer(AnswerText.WEATHER)


@weather_router.message(WeatherState.any_city_state, lambda message: not message.text.isnumeric())
async def weather_any_city(message: Message, state: FSMContext) -> None:
    weather_response = asyncio.create_task(WeatherApi.get_weather(message.text))
    result = await weather_response
    city = message.text
    if len(result) <= 2:
        await message.reply(AnswerText.WEATHER_WRONG_CITY.format(city=city))
    else:
        result = WeatherApi.parse_response(result, city)
        await message.reply(
            AnswerText.WEATHER_IN_ANY_CITY.format(result=result),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()


@weather_router.message(WeatherState.any_city_state)
async def weather_wrong_city(message: Message) -> None:
    await message.reply(AnswerText.WEATHER_WRONG_CITY.format(city=message.text))


@weather_router.message()
async def echo_handler(message: Message) -> None:
    main_keyboard = KeyboardBuilder.main_reply_keyboard()
    try:
        await message.send_copy(chat_id=message.chat.id, reply_markup=main_keyboard)
    except TypeError:
        await message.answer("Nice try!")
