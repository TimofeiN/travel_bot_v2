from enum import Enum

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot_utils import AnswerText, KeyboardBuilder
from data_providers.aviasales_api import AviasalesAPI, TicketResponse


class Destination(Enum):
    LED = "Snt-Petersburg"
    AER = "Sochi"
    KZN = "Kazan"


DESTINATION_MAP: dict[str, str] = {item.name: item.value for item in Destination}
DESTINATION_KEYBOARD: list[list[InlineKeyboardButton]] = [
    [InlineKeyboardButton(text=destination.value, callback_data=destination.name) for destination in Destination],
]


class DestinationLimit(StatesGroup):
    choosing_destination = State()
    choosing_limit = State()


class DestinationService:
    @staticmethod
    async def handle_destination_command(message: Message, state: FSMContext) -> None:
        destination_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=DESTINATION_KEYBOARD)
        await message.answer(text=AnswerText.DESTINATION, reply_markup=destination_inline_keyboard)
        await state.set_state(DestinationLimit.choosing_destination)

    @staticmethod
    async def handle_destination_selected(callback: CallbackQuery, state: FSMContext) -> None:
        await state.update_data(destination=callback.data)
        await callback.message.answer(text=AnswerText.DESTINATIONS_LIMIT)
        await state.set_state(DestinationLimit.choosing_limit)

    @staticmethod
    async def _send_destination_tickets(message: Message, tickets_response: list[TicketResponse]) -> None:
        for ticket in tickets_response:
            destination_code = ticket.destination
            subscription_data = f"subscription MOW {destination_code}"
            destination_name = DESTINATION_MAP.get(destination_code)

            reply_string = AnswerText.YOU_CAN_FLY.format(destination=destination_name, price=ticket.price, weather="")
            reply_keyboard = KeyboardBuilder.ticket_reply_keyboard(
                ticket_url=ticket.link, subscription_data=subscription_data
            )
            await message.answer(reply_string, reply_markup=reply_keyboard)

    @classmethod
    async def handle_limit_selected(cls, message: Message, state: FSMContext) -> None:
        selected_data = await state.get_data()
        limit = int(message.text)
        destination_code = selected_data.get("destination")

        url = AviasalesAPI.create_default_request_url(destination_code, limit)
        tickets_response = await AviasalesAPI.get_one_city_price(request_url=url)

        await message.answer(AnswerText.CHEAPEST)
        (
            await message.answer(AnswerText.NO_TICKETS)
            if not tickets_response
            else await cls._send_destination_tickets(message, tickets_response)
        )
        await state.clear()

    @staticmethod
    async def wrong_limit(message: Message) -> None:
        await message.answer(text=AnswerText.WRONG_LIMIT)


destination_router = Router()
destination_router.message.register(
    DestinationService.handle_destination_command, StateFilter(None), Command("destination")
)
destination_router.callback_query.register(
    DestinationService.handle_destination_selected,
    DestinationLimit.choosing_destination,
    lambda callback: callback.data in [destination.name for destination in Destination],
)
destination_router.message.register(
    DestinationService.handle_limit_selected,
    DestinationLimit.choosing_limit,
    lambda message: message.text.isdecimal() and int(message.text) < 10,
)
destination_router.message.register(DestinationService.wrong_limit, DestinationLimit.choosing_limit)
