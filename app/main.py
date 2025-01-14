import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot_utils.answers import answers
from bot_utils.keyboards import KeyboardBuilder
from services.destinations_service import destination_router
from services.five_cheapest_service import five_cheapest_router
from services.location_service import StartLocation, location_router
from services.season_tickets_service import season_ticket_router
from services.user_subscriptions import subscription_router
from services.weather_service import weather_router

TOKEN = os.environ.get("BOT_TOKEN")

dp = Dispatcher()


@dp.message(StateFilter(None), CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    location_keyboard = KeyboardBuilder.location_reply_keyboard()
    await message.answer(answers.start.format(username=message.from_user.username))
    await message.answer(answers.city_or_location, reply_markup=location_keyboard)

    await state.set_state(StartLocation.choosing_location)


@dp.message(Command("cancel"))
@dp.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(reply_markup=KeyboardBuilder.main_reply_keyboard(), text="Current action canceled.")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(location_router)
    dp.include_router(five_cheapest_router)
    dp.include_router(destination_router)
    dp.include_router(season_ticket_router)
    dp.include_router(subscription_router)
    dp.include_router(weather_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
