import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot_utils.answers import answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from data_providers.weather_api import WeatherApi
from database.db_api import DatabaseQueries

weather_router = Router()


class WeatherState(StatesGroup):
    any_city_state = State()


@weather_router.message(Command("weather"))
async def weather(message: Message) -> None:
    await weather_handler(message)


@weather_router.message(lambda message: message.text == buttons.weather)
async def weather_handler(message: Message) -> None:
    keyboard = KeyboardBuilder.weather_reply_keyboard()
    await message.answer(answers.weather_action, reply_markup=keyboard)


@weather_router.message(lambda message: message.text == buttons.weather_in_your_city)
async def your_city(message: Message):
    users_city_coords = await asyncio.create_task(DatabaseQueries.get_users_city(message.from_user.id))
    weather_your_city = asyncio.create_task(
        WeatherApi.get_weather_with_coor(
            users_city_coords[1],
            users_city_coords[2],
        )
    )
    result = await weather_your_city
    parsed_result = WeatherApi.parse_response(result, users_city_coords[0])
    await message.reply(
        answers.weather_in_your_city.format(result=parsed_result),
        reply_markup=KeyboardBuilder.main_reply_keyboard(),
    )


@weather_router.message(lambda message: message.text == buttons.weather_in_any_city)
async def any_city(message: Message, state: FSMContext) -> None:
    await state.set_state(WeatherState.any_city_state)
    await message.answer(answers.weather)


@weather_router.message(WeatherState.any_city_state, lambda message: not message.text.isnumeric())
async def weather_any_city(message: Message, state: FSMContext) -> None:
    weather_response = asyncio.create_task(WeatherApi.get_weather(message.text))
    result = await weather_response
    city = message.text
    if len(result) <= 2:
        await message.reply(answers.weather_wrong_city.format(city=city))
    else:
        result = WeatherApi.parse_response(result, city)
        await message.reply(
            answers.weather_in_any_city.format(result=result),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()


@weather_router.message(WeatherState.any_city_state)
async def weather_wrong_city(message: Message) -> None:
    await message.reply(answers.weather_wrong_city.format(city=message.text))


@weather_router.message()
async def echo_handler(message: Message) -> None:
    main_keyboard = KeyboardBuilder.main_reply_keyboard()
    try:
        await message.send_copy(chat_id=message.chat.id, reply_markup=main_keyboard)
    except TypeError:
        await message.answer("Nice try!")
