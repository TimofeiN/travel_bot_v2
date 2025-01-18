import asyncio
from dataclasses import asdict, dataclass

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot_utils import AirportFinder, AnswerText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI
from database import Airport, City, DatabaseAPI


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
        city_airports: list[Airport],
        message: Message,
        state: FSMContext,
        in_city: str,
        country: str,
        airport_name: str,
    ) -> None:
        if len(city_airports) == 1:
            await message.answer(
                AnswerText.LOCATION.format(in_city=in_city, country=country, airport=airport_name),
                reply_markup=KeyboardBuilder.main_reply_keyboard(),
            )
        else:
            airports_list = [airport.name for airport in city_airports]
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

        airport = await AirportFinder.find_closest_airport(user_coordinates)
        in_city, country = await AviasalesAPI.get_city_names_with_code(airport.city_code)
        city_airports = await DatabaseAPI.get_city_airports(airport.city_code)

        asyncio.create_task(DatabaseAPI.user_update_or_create(**asdict(user_data), city_id=airport.city_id))
        await cls.process_location_answer(
            city_airports=city_airports,
            message=message,
            state=state,
            in_city=in_city,
            country=country,
            airport_name=airport.name,
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
    async def process_select_from_two_answer(cities: list[City], state: FSMContext, message: Message) -> None:
        state_data = {city.code: city.name for city in cities}
        await state.update_data(state_data)

        await message.answer(
            text=AnswerText.TWO_CITIES,
            reply_markup=KeyboardBuilder.location_two_cities_keyboard(cities),
        )
        await state.set_state(StartLocation.choosing_city)

    @classmethod
    async def process_one_city_answer(
        cls, city: City, user_data: UserData, message: Message, state: FSMContext
    ) -> None:
        city_airports = await DatabaseAPI.get_city_airports(city.code)

        first_airport = city_airports[0]
        asyncio.create_task(DatabaseAPI.user_update_or_create(**asdict(user_data), city_id=first_airport.city_id))

        if len(city_airports) > 1:
            airports_list = [airport.name for airport in city_airports]
            airports_text = ", ".join(airports_list)
            await cls._answer_multi_airports_found(message, city.name, airports_text)
        else:
            await cls._answer_one_airport_found(message, city.name, first_airport.name)

        await state.clear()

    @classmethod
    async def handle_city_input(cls, message: Message, state: FSMContext) -> None:
        user_data = LocationProvidedService.get_user_data_from_message(message)
        cities = await DatabaseAPI.get_cities_by_name(city_name=message.text)

        if not cities:
            await cls.handle_city_not_found(message)
        elif len(cities) == 1:
            await cls.process_one_city_answer(city=cities[0], user_data=user_data, message=message, state=state)
        else:
            await cls.process_select_from_two_answer(cities, state, message)

    @classmethod
    async def handle_city_selected_from_two(cls, callback: CallbackQuery, state: FSMContext) -> None:
        user_data = LocationProvidedService.get_user_data_from_callback(callback)
        city_code = callback.data

        city_airports = await DatabaseAPI.get_city_airports(city_code)
        first_airport = city_airports[0]
        asyncio.create_task(DatabaseAPI.user_update_or_create(**asdict(user_data), city_id=first_airport.city_id))

        state_data = await state.get_data()
        city_name = state_data.get(city_code)

        if len(city_airports) == 1:
            await cls._answer_one_airport_found(callback.message, city_name, first_airport.name)

        else:
            airports_list = [airport.name for airport in city_airports]
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
