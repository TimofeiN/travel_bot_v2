import asyncio
import logging
import random
from typing import Final

from aiogram import Router
from aiogram.types import Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI, TicketResponse
from data_providers.weather_api import WeatherApi
from database import City, DatabaseAPI

NUMBER_OF_TICKETS: Final[int] = 5
TRUE_STRING: Final[str] = "true"

log = logging.getLogger(__name__)


class SeasonService:
    @staticmethod
    async def _request_api(batch: list[City], user_city: City, default_date: str) -> list[list[TicketResponse]]:
        ticket_tasks = []

        for city in batch:
            request_url = AviasalesAPI.create_custom_request_url(
                origin=user_city.code,
                destination=city.code,
                departure_date=default_date,
                unique=TRUE_STRING,
            )
            ticket_tasks.append(asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=request_url)))

        return await asyncio.gather(*ticket_tasks, return_exceptions=True)

    @staticmethod
    def _prepare_ticket_response(
        batch: list[City], tickets_response: list[list[TicketResponse]]
    ) -> tuple[list[City], list[TicketResponse]]:
        database_cities = []
        tickets = []
        batch_map = {city.code: city for city in batch}

        for ticket_obj in tickets_response:
            if not ticket_obj or isinstance(ticket_obj[0], Exception) or ticket_obj[0].destination is None:
                continue
            ticket = ticket_obj[0]
            city = batch_map.get(ticket.destination)
            if city:
                tickets.append(ticket)
                database_cities.append(city)

        return database_cities, tickets

    @classmethod
    async def _get_available_tickets(
        cls, user_city: City, cities: list[City]
    ) -> tuple[list[City], list[TicketResponse]]:
        default_date = AviasalesAPI.get_default_dates()
        database_cities = []
        tickets = []

        while cities and len(tickets) < NUMBER_OF_TICKETS:
            range_number = min(NUMBER_OF_TICKETS, len(cities))
            batch = [cities.pop() for _ in range(range_number)]
            if not batch:
                continue

            tickets_response = await cls._request_api(batch, user_city, default_date)
            if not tickets_response:
                continue

            database_batch, ticket_batch = cls._prepare_ticket_response(batch, tickets_response)
            database_cities.extend(database_batch)
            tickets.extend(ticket_batch)

        return database_cities, tickets

    @staticmethod
    async def _send_season_messages(
        message: Message, database_cities: list[City], tickets: list[TicketResponse], user_city: City
    ) -> None:
        for city, ticket in zip(database_cities, tickets):
            weather_response = await WeatherApi.get_weather_with_coor(city.latitude, city.longitude)
            weather_data = WeatherApi.small_parse_response(weather_response)
            subscription_data = f"subscription {user_city.code} {ticket.destination}"

            reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket.link, subscription_data)
            answer_string = AnswerText.YOU_CAN_FLY.format(
                destination=city.name,
                price=ticket.price,
                weather=weather_data,
            )
            await message.answer(answer_string, reply_markup=reply_keyboard)

    @classmethod
    async def season_handler(cls, message: Message) -> None:
        user_city = await DatabaseAPI.get_user_city(message.from_user.id)
        summer_season_cities = await DatabaseAPI.get_summer_season_cities()
        random.shuffle(summer_season_cities)
        log.info(f"Fetched {len(summer_season_cities)} season cities.")

        database_cities, tickets = await cls._get_available_tickets(user_city, summer_season_cities)

        await message.answer(AnswerText.SEASON)
        await cls._send_season_messages(
            message=message, database_cities=database_cities, tickets=tickets, user_city=user_city
        )


season_ticket_router = Router()
season_ticket_router.message.register(SeasonService.season_handler, lambda message: message.text == ButtonText.SEASON)
