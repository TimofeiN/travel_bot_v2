from aiogram import Router
from aiogram.types import CallbackQuery, Message

from bot_utils import AnswerText, ButtonText, KeyboardBuilder
from database import DatabaseAPI, Subscription


class UserSubscriptionsService:
    @staticmethod
    async def _send_subscriptions_messages(message: Message, subscriptions: list[Subscription]) -> None:
        for subscription in subscriptions:
            departure_city = await DatabaseAPI.get_city_by_code(subscription.departure_city_code)
            arrival_city = await DatabaseAPI.get_city_by_code(subscription.arrival_city_code)

            answer_text = AnswerText.SUBSCRIPTION.format(origin=departure_city.name, arrival=arrival_city.name)
            data = f"unsubscribe {subscription.departure_city_code} {subscription.arrival_city_code}"
            inline_keyboard = KeyboardBuilder.delete_subscription(data)

            await message.answer(answer_text, reply_markup=inline_keyboard)

    @classmethod
    async def handle_subscription_button(cls, message: Message) -> None:
        user_subscriptions = await DatabaseAPI.get_user_subscriptions(message.from_user.id)

        if not user_subscriptions:
            await message.answer(AnswerText.NO_SUBSCRIPTIONS)
        else:
            await cls._send_subscriptions_messages(message, user_subscriptions)

    @classmethod
    async def unsubscribe(cls, callback: CallbackQuery) -> None:
        data = callback.data.split()
        await DatabaseAPI.delete_subscription(
            user_id=callback.from_user.id, origin_code=data[1], destination_code=data[2]
        )
        await callback.message.answer(AnswerText.UNSUBSCRIPTION)
        await cls.handle_subscription_button(callback.message)

    @staticmethod
    async def subscribe(callback: CallbackQuery) -> None:
        data = callback.data.split()
        await DatabaseAPI.create_subscription(callback.from_user.id, data[1], data[2])
        await callback.message.answer(AnswerText.SUBSCRIBED)


subscription_router = Router()
subscription_router.message.register(
    UserSubscriptionsService.handle_subscription_button, lambda message: message.text == ButtonText.SUBSCRIPTIONS
)
subscription_router.callback_query.register(
    UserSubscriptionsService.unsubscribe, lambda callback: callback.data.split()[0] == "unsubscribe"
)
subscription_router.callback_query.register(
    UserSubscriptionsService.subscribe, lambda callback: callback.data.split()[0] == "subscription"
)
