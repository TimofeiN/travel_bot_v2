from enum import Enum
from typing import Optional

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot_utils import AnswerText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI


class Destination(Enum):
    LED = "Snt-Petersburg"
    AER = "Sochi"
    KZN = "Kazan"


DESTINATION_MAP: dict[str, str] = {item.name: item.value for item in Destination}
DESTINATION_KEYBOARD: list[list[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(text=Destination.LED.value, callback_data=Destination.LED.name),
        InlineKeyboardButton(text=Destination.AER.value, callback_data=Destination.AER.name),
        InlineKeyboardButton(text=Destination.KZN.value, callback_data=Destination.KZN.name),
    ],
]

destination_router = Router()


class DestinationLimit(StatesGroup):
    choosing_destination = State()
    choosing_limit = State()


@destination_router.message(StateFilter(None), Command("destination"))
async def destination_choose_city(message: Message, state: FSMContext) -> None:
    destination_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=DESTINATION_KEYBOARD)
    await message.answer(text=AnswerText.DESTINATION, reply_markup=destination_inline_keyboard)
    await state.set_state(DestinationLimit.choosing_destination)


@destination_router.callback_query(
    DestinationLimit.choosing_destination,
    lambda callback: callback.data in [destination for destination in Destination],
)
async def choose_destination(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(destination=callback.data)
    await callback.message.answer(text=AnswerText.LIMIT)
    await state.set_state(DestinationLimit.choosing_limit)


@destination_router.message(
    DestinationLimit.choosing_limit,
    lambda message: message.text.isdecimal() and int(message.text) < 10,
)
async def choose_limit(message: Message, state: FSMContext) -> Optional[Message]:
    await state.update_data(limit=message.text)
    user_data = await state.get_data()
    url = AviasalesAPI.create_default_request_url(user_data["destination"], user_data["limit"])
    result = await AviasalesAPI.get_one_city_price(request_url=url)

    await message.answer(AnswerText.CHEAPEST)

    if not result:
        await state.clear()
        return await message.answer(AnswerText.NO_TICKETS)

    for destination in result:
        ticket_url = destination.link
        price = destination.price
        destination_code = destination.destination
        destination_name = DESTINATION_MAP.get(destination_code)

        reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(ticket_url)
        reply_string = AnswerText.YOU_CAN_FLY.format(destination=destination_name, price=price, weather="weather")
        await message.answer(reply_string, reply_markup=reply_keyboard)

    await state.clear()


@destination_router.message(DestinationLimit.choosing_limit)
async def wrong_limit(message: Message) -> None:
    await message.answer(text=AnswerText.WRONG_LIMIT)
