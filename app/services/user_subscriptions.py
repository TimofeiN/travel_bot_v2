from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from database import DatabaseAPI

subscription_router = Router()


@subscription_router.message(lambda message: message.text == ButtonText.SUBSCRIPTIONS)
async def show_subscriptions(message: Message) -> None:
    subscriptions = await DatabaseAPI.get_user_subscriptions(message.from_user.id)

    if subscriptions:
        await message.answer(AnswerText.SUBSCRIPTION)
        for subscription in subscriptions:
            origin = await DatabaseAPI.get_city_by_code(subscription.departure_city_code)
            arrival = await DatabaseAPI.get_city_by_code(subscription.arrival_city_code)
            answer_text = AnswerText.SUBSCRIPTION.format(origin=origin.name, arrival=arrival.name)
            data = f"unsubscribe {subscription.departure_city_code} {subscription.arrival_city_code}"
            await message.answer(answer_text, reply_markup=KeyboardBuilder.delete_subscription(data))
    else:
        await message.answer(AnswerText.NO_SUBSCRIPTIONS)


@subscription_router.callback_query(lambda callback: callback.data.split()[0] == "unsubscribe")
async def unsubscribe(callback: CallbackQuery) -> None:
    data = callback.data.split()
    await DatabaseAPI.delete_subscription(user_id=callback.from_user.id, origin_code=data[1], destination_code=data[2])
    await callback.message.answer(AnswerText.UNSUBSCRIPTION)
    await show_subscriptions(callback.message)


@subscription_router.callback_query(lambda callback: callback.data.split()[0] == "subscription")
async def subscribe(callback: CallbackQuery) -> None:
    data = callback.data.split()
    await DatabaseAPI.create_subscription(callback.from_user.id, data[1], data[2])
    await callback.message.answer(AnswerText.SUBSCRIBE)
