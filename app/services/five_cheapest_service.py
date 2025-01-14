import asyncio

from aiogram import Router
from aiogram.types import Message

from bot_utils.answers import Answers
from bot_utils.buttons import buttons
from bot_utils.keyboards import KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI
from data_providers.weather_api import WeatherApi
from database.db_api import DatabaseQueries

five_cheapest_router = Router()
answers = Answers


@five_cheapest_router.message(lambda message: message.text == buttons.five_cheapest)
async def five_cheapest_handler(message: Message) -> None:
    users_city = await asyncio.create_task(DatabaseQueries.get_users_city(message.from_user.id))
    origin = users_city[3]
    default_date = AviasalesAPI.get_default_dates()
    request_url = AviasalesAPI.create_custom_request_url(
        origin=origin, departure_date=default_date, unique="true", limit=5
    )
    task_get_five = asyncio.create_task(AviasalesAPI.get_one_city_price(request_url=request_url))
    result = await task_get_five
    await message.answer(answers.cheapest)

    for destination in result:
        ticket_url = destination.get("link", "")
        destination_city = await asyncio.create_task(DatabaseQueries.city_by_code(destination["destination"]))
        if not destination_city:
            continue
        subscription_data = f"subscription {origin} {destination['destination']}"
        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url, subscription_data)

        weather_city = asyncio.create_task(WeatherApi.get_weather_with_coor(destination_city[1], destination_city[2]))
        result = await weather_city
        parsed_result = WeatherApi.small_parse_response(result) if result else ""
        answer_string = answers.you_can_fly.format(
            destination=destination_city[0],
            price=destination["price"],
            weather=parsed_result,
        )

        await message.answer(answer_string, reply_markup=reply_keyboard)
