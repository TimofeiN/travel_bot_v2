import asyncio
from typing import Any

from aiogram import Router
from aiogram.types import Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI
from data_providers.weather_api import WeatherApi
from database.db_api import DatabaseQueries


class FiveCheapestService:
    @staticmethod
    async def send_ticket_message(
        destination: dict[str, Any],
        database_city: tuple,
        weather_response: dict[str, Any],
        message: Message,
        origin_code: str,
    ) -> None:
        ticket_price = destination.get("price")
        destination_city_name = database_city[0]
        weather_short_response = WeatherApi.small_parse_response(weather_response) if weather_response else ""
        answer_string = AnswerText.YOU_CAN_FLY.format(
            destination=destination_city_name,
            price=ticket_price,
            weather=weather_short_response,
        )

        destination_code = destination.get("destination")
        ticket_url = destination.get("link", "")
        subscription_data = f"subscription {origin_code} {destination_code}"
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url, subscription_data)

        await message.answer(answer_string, reply_markup=reply_keyboard)

    @classmethod
    async def process_five_cheapest(
        cls, five_cheapest_response: list[dict[str, Any]], message: Message, origin_code: str
    ) -> None:
        database_city_tasks = [
            asyncio.create_task(DatabaseQueries.city_by_code(destination["destination"]))
            for destination in five_cheapest_response
        ]
        database_cities = await asyncio.gather(*database_city_tasks)

        weather_tasks = [
            asyncio.create_task(WeatherApi.get_weather_with_coor(destination_city[1], destination_city[2]))
            for destination_city in database_cities
        ]
        weather_results = await asyncio.gather(*weather_tasks)
        for destination, database_city, weather_response in zip(
            five_cheapest_response, database_cities, weather_results
        ):
            if not database_city:
                continue

            await cls.send_ticket_message(
                destination=destination,
                database_city=database_city,
                weather_response=weather_response,
                message=message,
                origin_code=origin_code,
            )

    @classmethod
    async def handle_message(cls, message: Message) -> None:
        user_city = await DatabaseQueries.get_users_city(message.from_user.id)
        origin_code = user_city[3]
        default_date = AviasalesAPI.get_default_dates()
        request_url = AviasalesAPI.create_custom_request_url(
            origin=origin_code, departure_date=default_date, unique="true", limit=5
        )
        five_cheapest_response = await AviasalesAPI.get_one_city_price(request_url=request_url)
        await message.answer(AnswerText.CHEAPEST)
        await cls.process_five_cheapest(five_cheapest_response, message, origin_code)


five_cheapest_router = Router()
five_cheapest_router.message.register(
    FiveCheapestService.handle_message, lambda message: message.text == ButtonText.FIVE_CHEAPEST
)
