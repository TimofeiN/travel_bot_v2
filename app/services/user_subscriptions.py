from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from database.db_api import DatabaseQueries

subscription_router = Router()


@subscription_router.message(lambda message: message.text == ButtonText.SUBSCRIPTIONS)
async def show_subscriptions(message: Message) -> None:
    user_id = message.chat.id
    subscriptions = await DatabaseQueries.user_subscriptions(user_id)

    if subscriptions:
        await message.answer(AnswerText.SUBSCRIPTION)
        for subscription in subscriptions:
            origin = await DatabaseQueries.city_by_code(subscription[0])
            arrival = await DatabaseQueries.city_by_code(subscription[1])
            answer_text = AnswerText.SUBSCRIPTION.format(origin=origin[0], arrival=arrival[0])
            data = f"unsubscribe {subscription[0]} {subscription[1]}"
            await message.answer(answer_text, reply_markup=KeyboardBuilder.delete_subscription(data))
    else:
        await message.answer(AnswerText.NO_SUBSCRIPTIONS)


@subscription_router.callback_query(lambda callback: callback.data.split()[0] == "unsubscribe")
async def unsubscribe(callback: CallbackQuery) -> None:
    data = callback.data.split()
    await DatabaseQueries.unsubscription(callback.from_user.id, data[1], data[2])
    await callback.message.answer(AnswerText.UNSUBSCRIPTION)
    await show_subscriptions(callback.message)


@subscription_router.callback_query(lambda callback: callback.data.split()[0] == "subscription")
async def subscribe(callback: CallbackQuery) -> None:
    data = callback.data.split()
    await DatabaseQueries.subscription(callback.from_user.id, data[1], data[2])
    await callback.message.answer(AnswerText.SUBSCRIBE)
