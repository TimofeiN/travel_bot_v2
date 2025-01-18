import asyncio
from typing import Any

from aiogram import Router
from aiogram.types import Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI, TicketResponse
from data_providers.weather_api import WeatherApi
from database import City, DatabaseAPI


class FiveCheapestService:
    @staticmethod
    async def send_ticket_message(
        ticket: TicketResponse,
        database_city: City,
        weather_response: dict[str, Any],
        message: Message,
        origin_code: str,
    ) -> None:
        destination_city_name = database_city.name
        weather_short_response = WeatherApi.small_parse_response(weather_response) if weather_response else ""
        answer_string = AnswerText.YOU_CAN_FLY.format(
            destination=destination_city_name,
            price=ticket.price,
            weather=weather_short_response,
        )

        destination_code = ticket.destination
        ticket_url = ticket.link
        subscription_data = f"subscription {origin_code} {destination_code}"
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url, subscription_data)

        await message.answer(answer_string, reply_markup=reply_keyboard)

    @classmethod
    async def process_five_cheapest(
        cls, five_cheapest_response: list[TicketResponse], message: Message, origin_code: str
    ) -> None:
        database_city_tasks = [
            asyncio.create_task(DatabaseAPI.get_city_by_code(city_code=ticket.destination))
            for ticket in five_cheapest_response
            if ticket
        ]
        database_cities = await asyncio.gather(*database_city_tasks)

        weather_tasks = [
            asyncio.create_task(WeatherApi.get_weather_with_coor(destination_city.latitude, destination_city.longitude))
            for destination_city in database_cities
            if destination_city
        ]
        weather_results = await asyncio.gather(*weather_tasks)

        for ticket, database_city, weather_response in zip(five_cheapest_response, database_cities, weather_results):
            all_objects_exist = ticket and database_city and weather_response
            if not all_objects_exist:
                continue

            await cls.send_ticket_message(
                ticket=ticket,
                database_city=database_city,
                weather_response=weather_response,
                message=message,
                origin_code=origin_code,
            )

    @classmethod
    async def handle_message(cls, message: Message) -> None:
        user_city = await DatabaseAPI.get_user_city(user_id=message.from_user.id)
        default_date = AviasalesAPI.get_default_dates()
        request_url = AviasalesAPI.create_custom_request_url(
            origin=user_city.code, departure_date=default_date, unique="true", limit=5
        )
        five_cheapest_response = await AviasalesAPI.get_one_city_price(request_url=request_url)
        await message.answer(AnswerText.CHEAPEST)
        await cls.process_five_cheapest(five_cheapest_response, message, user_city.code)


five_cheapest_router = Router()
five_cheapest_router.message.register(
    FiveCheapestService.handle_message, lambda message: message.text == ButtonText.FIVE_CHEAPEST
)
