import os

from aiohttp import ClientSession


class WeatherApi:
    TOKEN = os.environ.get("OPEN_WEATHER_TOKEN")

    weather_icon = {
        "Clear": "\U00002600",
        "Clouds": "\U00002601",
        "Rain": "\U00002614",
        "Drizzle": "\U00002614",
        "Thunderstorm": "\U000026A1",
        "Snow": "\U0001F328",
        "Mist": "\U0001F32B",
        "Fog": "",
        "Haze": "",
    }

    @classmethod
    def parse_response(cls, response: dict, city) -> str:
        return (
            f"Погода в городе {city}:\n"
            f'{response["weather"][0]["description"].capitalize()}'
            f'{cls.weather_icon.get(response["weather"][0]["main"], "")} \n'
            f'Температура: {response["main"]["temp"]}C°\n'
            f'Ощущается как: {response["main"]["feels_like"]}C°\n'
            f'Влажность: {response["main"]["humidity"]}%\n'
            f'Давление: {response["main"]["pressure"]}мм.рт.ст\n'
            f'Ветер: {response["wind"]["speed"]}м/с'
        )

    @classmethod
    def small_parse_response(cls, response: dict) -> str:
        return (
            f'{response["weather"][0]["description"].capitalize()}'
            f'{cls.weather_icon.get(response["weather"][0]["main"])} \n'
            f'Температура: {response["main"]["temp"]}C°\n'
            f'Влажность: {response["main"]["humidity"]}%\n'
        )

    @classmethod
    async def get_weather_with_coor(cls, lat, lon):
        async with ClientSession() as session:
            async with session.get(
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"lat={lat}&lon={lon}&appid={cls.TOKEN}&units=metric&lang=ru"
            ) as response:
                data = await response.json()
                return data

    @classmethod
    async def get_weather(cls, city):
        async with ClientSession() as session:
            async with session.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={cls.TOKEN}&units=metric&lang=ru"
            ) as response:
                data = await response.json()
                return data
