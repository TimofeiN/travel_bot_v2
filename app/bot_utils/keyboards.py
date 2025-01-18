from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from database import City

from .bot_texts import ButtonText


class KeyboardBuilder:
    @staticmethod
    def location_reply_keyboard() -> ReplyKeyboardMarkup:
        location_keyboard_buttons = [
            [
                KeyboardButton(text=ButtonText.LOCATION, request_location=True),
            ],
        ]
        return ReplyKeyboardMarkup(
            keyboard=location_keyboard_buttons,
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    @staticmethod
    def location_two_cities_keyboard(cities: list[City]) -> InlineKeyboardMarkup:
        ticket_keyboard_buttons = [
            [
                InlineKeyboardButton(text=f"{city.name} ({city.country_code})", callback_data=city.code)
                for city in cities
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=ticket_keyboard_buttons)

    @staticmethod
    def main_reply_keyboard() -> ReplyKeyboardMarkup:
        main_keyboard_buttons = [
            [
                KeyboardButton(text=ButtonText.SUBSCRIPTIONS),
                KeyboardButton(text=ButtonText.FIVE_CHEAPEST),
                KeyboardButton(text=ButtonText.WEATHER),
                KeyboardButton(text=ButtonText.SEASON),
            ],
        ]
        return ReplyKeyboardMarkup(
            keyboard=main_keyboard_buttons,
            resize_keyboard=True,
            one_time_keyboard=False,
        )

    @staticmethod
    def ticket_reply_keyboard(ticket_url: str, subscription_data: str = None) -> InlineKeyboardMarkup:
        ticket_keyboard_buttons = [
            [
                InlineKeyboardButton(text=ButtonText.BUY, url=ticket_url),
                InlineKeyboardButton(text=ButtonText.SUBSCRIBE, callback_data=subscription_data),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=ticket_keyboard_buttons)

    @staticmethod
    def delete_subscription(data) -> InlineKeyboardMarkup:
        delete_subscription_keyboard = [
            [InlineKeyboardButton(text=ButtonText.UNSUBSCRIBE, callback_data=data)],
        ]
        return InlineKeyboardMarkup(inline_keyboard=delete_subscription_keyboard)

    @staticmethod
    def weather_reply_keyboard() -> ReplyKeyboardMarkup:
        weather_keyboard = [
            [
                KeyboardButton(text=ButtonText.WEATHER_IN_YOUR_CITY),
                KeyboardButton(text=ButtonText.WEATHER_IN_ANY_CITY),
            ],
        ]
        return ReplyKeyboardMarkup(keyboard=weather_keyboard, resize_keyboard=True)

    @staticmethod
    def season_reply_keyboard() -> ReplyKeyboardMarkup:
        season_keyboard = [
            [KeyboardButton(text=ButtonText.SEASON)],
        ]
        return ReplyKeyboardMarkup(keyboard=season_keyboard, resize_keyboard=True)
