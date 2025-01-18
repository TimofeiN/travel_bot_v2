import asyncio
import logging
import random

from aiogram import Router
from aiogram.types import Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI
from data_providers.weather_api import WeatherApi
from database import DatabaseAPI
from database.db_api import DatabaseQueries

log = logging.getLogger(__name__)
season_ticket_router = Router()


@season_ticket_router.message(lambda message: message.text == ButtonText.SEASON)
async def season_handler(message: Message) -> None:
    ticket_list = []
    user_city = await DatabaseAPI.get_user_city(message.from_user.id)
    summer_season_cities = await DatabaseQueries.cities_where_the_season()
    log.info(len(summer_season_cities))
    random_cities_where_season = random.sample(summer_season_cities, len(summer_season_cities))

    for city in random_cities_where_season:
        default_date = AviasalesAPI.get_default_dates()
        request_url = AviasalesAPI.create_custom_request_url(
            origin=user_city.code,
            destination=city[0],
            departure_date=default_date,
            unique="true",
            limit=1,
        )

        response = asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=request_url))
        result = await response
        if result:
            log.info(result)
            ticket = {
                "ticket_url": result[0].link,
                "price": result[0].price,
                "destination": city[1],
                "lat": city[2],
                "lon": city[3],
                "destination_code": city[0],
            }
            ticket_list.append(ticket)
            if len(ticket_list) == 5:
                break

    await message.answer(AnswerText.SEASON)
    for ticket in ticket_list:
        subscription_data = f"subscription {user_city.code} {ticket['destination_code']}"
        weather_city = asyncio.create_task(WeatherApi.get_weather_with_coor(ticket["lat"], ticket["lon"]))
        result = await weather_city
        parsed_result = WeatherApi.small_parse_response(result)
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket["ticket_url"], subscription_data)
        answer_string = AnswerText.SEASON_WEATHER.format(
            destination=ticket["destination"],
            price=ticket["price"],
            weather=parsed_result,
        )

        await message.answer(answer_string, reply_markup=reply_keyboard)
