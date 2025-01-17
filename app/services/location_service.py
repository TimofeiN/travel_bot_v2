import asyncio
from dataclasses import asdict, dataclass
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot_utils import AirportFinder, AnswerText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI
from database.db_api import DatabaseQueries


@dataclass
class UserData:
    user_id: int
    username: str
    chat_id: int


class StartLocation(StatesGroup):
    choosing_location = State()
    choosing_city = State()


class LocationProvidedService:
    @staticmethod
    def get_user_data_from_message(message: Message) -> UserData:
        return UserData(user_id=message.from_user.id, username=message.from_user.username, chat_id=message.chat.id)

    @staticmethod
    def get_user_data_from_callback(callback: CallbackQuery) -> UserData:
        return UserData(
            user_id=callback.from_user.id, username=callback.from_user.username, chat_id=callback.message.chat.id
        )

    @staticmethod
    async def process_location_answer(
        count_airports_response: list[Any],
        message: Message,
        state: FSMContext,
        in_city: str,
        country: str,
        airport_name: str,
    ) -> None:
        if len(count_airports_response) == 1:
            await message.answer(
                AnswerText.LOCATION.format(in_city=in_city, country=country, airport=airport_name),
                reply_markup=KeyboardBuilder.main_reply_keyboard(),
            )
        else:
            airports_list = [name[0] for name in count_airports_response]
            airports_text = ", ".join(airports_list)
            answer_text = AnswerText.LOCATION_MANY.format(
                in_city=in_city,
                country=country,
                airport=airport_name,
                airports=airports_text,
            )
            await message.answer(answer_text, reply_markup=KeyboardBuilder.main_reply_keyboard())

        await state.clear()

    @classmethod
    async def handle_location(cls, message: Message, state: FSMContext) -> None:
        user_data = cls.get_user_data_from_message(message)
        user_coordinates = (message.location.latitude, message.location.longitude)

        airport_name, city_code = await AirportFinder.find_nearest_airport(user_coordinates)
        in_city, country = await AviasalesAPI.get_city_names_with_code(city_code)
        count_airports_response = await DatabaseQueries.count_airports_in_city_by_code(city_code)
        city_id = count_airports_response[0][3]

        asyncio.create_task(DatabaseQueries.user_update_or_create(**asdict(user_data), city_id=city_id))
        await cls.process_location_answer(
            count_airports_response=count_airports_response,
            message=message,
            state=state,
            in_city=in_city,
            country=country,
            airport_name=airport_name,
        )


class CityInputService:
    @staticmethod
    async def handle_city_not_found(message: Message) -> None:
        await message.answer(AnswerText.CITY_WITH_AIRPORT_NOT_FOUND)
        await message.answer(
            AnswerText.CITY_OR_LOCATION,
            reply_markup=KeyboardBuilder.location_reply_keyboard(),
        )

    @staticmethod
    async def _answer_one_airport_found(message: Message, city_name: str, airport_name: str) -> None:
        await message.answer(
            AnswerText.CITY_FOUND.format(city_name=city_name, airport_name=airport_name),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )

    @staticmethod
    async def _answer_multi_airports_found(message: Message, city_name: str, airports_text: str) -> None:
        await message.answer(
            AnswerText.CITIES_FOUND.format(city_name=city_name, airports_names=airports_text),
            reply_markup=KeyboardBuilder.main_reply_keyboard(),
        )

    @staticmethod
    async def process_select_from_two_answer(cities: list[tuple[Any]], state: FSMContext, message: Message) -> None:
        city_one = cities[0]
        city_two = cities[1]
        await state.update_data({city_one[1]: city_one[0], city_two[1]: city_two[0]})
        await message.answer(
            text=AnswerText.TWO_CITIES,
            reply_markup=KeyboardBuilder.location_two_cities_keyboard(city_one, city_two),
        )
        await state.set_state(StartLocation.choosing_city)

    @classmethod
    async def process_one_city_answer(
        cls, cities: list[tuple[Any]], user_data: UserData, message: Message, state: FSMContext
    ) -> None:
        city_name = cities[0][0]
        city_code = cities[0][1]
        count_airports_response = await DatabaseQueries.count_airports_in_city_by_code(city_code)
        city_id = count_airports_response[0][3]
        asyncio.create_task(DatabaseQueries.user_update_or_create(**asdict(user_data), city_id=city_id))

        if len(count_airports_response) > 1:
            airports_list = [name[2] for name in count_airports_response]
            airports_text = ", ".join(airports_list)
            await cls._answer_multi_airports_found(message, city_name, airports_text)
        else:
            airport_name = count_airports_response[0][2]
            await cls._answer_one_airport_found(message, city_name, airport_name)

        await state.clear()

    @classmethod
    async def handle_city_input(cls, message: Message, state: FSMContext) -> None:
        user_data = LocationProvidedService.get_user_data_from_message(message)
        cities = await DatabaseQueries.find_airports_by_city_name(message.text)

        if not cities:
            await cls.handle_city_not_found(message)
        elif len(cities) == 1:
            await cls.process_one_city_answer(cities=cities, user_data=user_data, message=message, state=state)
        else:
            await cls.process_select_from_two_answer(cities, state, message)

    @classmethod
    async def handle_city_selected_from_two(cls, callback: CallbackQuery, state: FSMContext) -> None:
        user_data = LocationProvidedService.get_user_data_from_callback(callback)
        city_code = callback.data

        count_airports_response = await DatabaseQueries.count_airports_in_city_by_code(city_code)
        city_id = count_airports_response[0][3]
        asyncio.create_task(DatabaseQueries.user_update_or_create(**asdict(user_data), city_id=city_id))

        state_data = await state.get_data()
        city_name = state_data.get(city_code)

        if len(count_airports_response) == 1:
            airport_name = count_airports_response[0][2]
            await cls._answer_one_airport_found(callback.message, city_name, airport_name)

        else:
            airports_list = [row[0] for row in count_airports_response]
            airports_text = ", ".join(airports_list)
            await cls._answer_multi_airports_found(callback.message, city_name, airports_text)

        await state.clear()


location_router = Router()
location_router.message.register(
    LocationProvidedService.handle_location, StartLocation.choosing_location, F.content_type == "location"
)
location_router.message.register(
    CityInputService.handle_city_input, StartLocation.choosing_location, lambda message: message.text
)
location_router.callback_query.register(CityInputService.handle_city_selected_from_two, StartLocation.choosing_city)
location_router.message(CityInputService.handle_city_not_found, StartLocation.choosing_city)
