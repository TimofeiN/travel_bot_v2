import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot_utils.answers import Answers
from bot_utils.find_airport import AirportFinder
from bot_utils.keyboards import KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI
from database.db_api import DatabaseQueries

location_router = Router()
answers = Answers


class StartLocation(StatesGroup):
    choosing_location = State()
    choosing_city = State()


@location_router.message(StartLocation.choosing_location, F.content_type == "location")
async def location(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    user_coords = (message.location.latitude, message.location.longitude)
    airport_name, city_code = await asyncio.create_task(AirportFinder.find_nearest_airport(user_coords))

    response_city_info = asyncio.create_task(AviasalesAPI.get_city_names_with_code(city_code))
    in_city, country = await response_city_info

    count_airports = await asyncio.create_task(DatabaseQueries.count_airports_in_city_by_code(city_code))
    city_id = count_airports[0][3]
    await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))
    if len(count_airports) > 1:
        airports_list = []
        for name in count_airports:
            airports_list.append(name[0])
        airports_text = ", ".join(airports_list)
        await message.answer(
            answers.location_many.format(
                in_city=in_city,
                country=country,
                airport=airport_name,
                airports=airports_text,
            ),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()
    else:
        await message.answer(
            answers.location.format(in_city=in_city, country=country, airport=airport_name),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()


@location_router.message(StartLocation.choosing_location, lambda message: message.text)
async def city_input(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    cities = await asyncio.create_task(DatabaseQueries.find_airports_by_city_name(message.text))
    if not cities:
        await message.answer(answers.city_with_airport_not_found)
        await message.answer(
            answers.city_or_location,
            reply_markup=KeyboardBuilder.location_reply_keyboard(),
        )
    elif len(cities) > 1:
        city_one = cities[0]
        city_two = cities[1]
        await state.update_data({city_one[1]: city_one[0], city_two[1]: city_two[0]})
        await message.answer(
            text=answers.two_cities,
            reply_markup=KeyboardBuilder.location_two_cities_keyboard(city_one, city_two),
        )
        await state.set_state(StartLocation.choosing_city)
    else:
        city_name = cities[0][0]
        city_code = cities[0][1]
        count_airports = await asyncio.create_task(DatabaseQueries.count_airports_in_city_by_code(city_code))
        city_id = count_airports[0][3]
        await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))
        if len(count_airports) > 1:
            airports_list = []
            for name in count_airports:
                airports_list.append(name[2])
            airports_text = ", ".join(airports_list)
            await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))
            await message.answer(
                answers.cities_found.format(city_name=city_name, airports_names=airports_text),
                reply_markup=KeyboardBuilder.main_reply_keyboard(),
            )
            await state.clear()
        else:
            airport_name = count_airports[0][2]
            await message.answer(
                answers.city_found.format(city_name=city_name, airport_name=airport_name),
                reply_markup=KeyboardBuilder.main_reply_keyboard(),
            )
            await state.clear()


@location_router.callback_query(StartLocation.choosing_city)
async def city_selected_from_two(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    username = callback.from_user.username
    chat_id = callback.message.chat.id

    city_code = callback.data
    data = await state.get_data()
    city_name = data[city_code]

    count_airports = await asyncio.create_task(DatabaseQueries.count_airports_in_city_by_code(city_code))
    city_id = count_airports[0][3]
    await asyncio.create_task(DatabaseQueries.insert_new_user(user_id, username, chat_id, city_id))

    if len(count_airports) > 1:
        airports_list = []
        for name in count_airports:
            airports_list.append(name[0])
        airports_text = ", ".join(airports_list)
        await callback.message.answer(
            answers.cities_found.format(city_name=city_name, airports_names=airports_text),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()
    else:
        airport_name = count_airports[0][2]
        await callback.message.answer(
            answers.city_found.format(city_name=city_name, airport_name=airport_name),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )
        await state.clear()


@location_router.message(StartLocation.choosing_city)
async def airport_not_found(message: Message) -> None:
    await message.answer(answers.city_or_location, reply_markup=KeyboardBuilder.location_reply_keyboard())
