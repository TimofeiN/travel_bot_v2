import datetime
from dataclasses import dataclass
from typing import Final, Optional

from aiohttp import ClientSession
from dateutils import relativedelta

from config.settings import AVIASALES_TOKEN

ERROR_STRING: Final[str] = "error"


@dataclass
class TicketResponse:
    destination: Optional[str] = None
    price: Optional[int] = None
    link: Optional[str] = None


class AviasalesAPI:
    @staticmethod
    def get_default_dates() -> str:
        this_date = datetime.date.today()
        if this_date.day < 20:
            return this_date.strftime("%Y-%m")
        next_month_date = this_date + relativedelta(months=1)
        return next_month_date.strftime("%Y-%m")

    @classmethod
    def create_default_request_url(cls, destination: str, limit: int = 1, departure_date: str = None) -> str:
        month = cls.get_default_dates()
        if not departure_date:
            departure_date = month
        return (
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin=MOW&destination={destination}"
            f"&departure_at={departure_date}&unique=false&sorting=price&direct=false"
            f"&cy=rub&limit={limit}&page=1&one_way=true&token={AVIASALES_TOKEN}"
        )

    @classmethod
    def create_custom_request_url(
        cls,
        origin: str = "MOW",
        destination: str = "",
        departure_date: str = "",
        return_date: str = "",
        unique: str = "false",
        direct: str = "false",
        limit: int = 1,
        one_way: str = "true",
    ) -> str:
        return (
            f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin={origin}&destination={destination}"
            f"&departure_at={departure_date}&return_at={return_date}&unique={unique}&sorting=price&direct={direct}"
            f"&cy=rub&limit={limit}&page=1&one_way={one_way}&token={AVIASALES_TOKEN}"
        )

    @classmethod
    def _parse_response(cls, api_response: dict) -> TicketResponse:
        link = "https://www.aviasales.ru" + api_response.get("link")
        destination = api_response.get("destination")
        price = api_response.get("price")
        return TicketResponse(destination=destination, price=price, link=link)

    @classmethod
    async def get_one_city_price(cls, request_url: str) -> Optional[list[TicketResponse]]:
        async with ClientSession() as session:
            async with session.get(request_url) as request:
                response = await request.json()
                response_data = response.get("data")
                if not response_data or ERROR_STRING in response_data:
                    return None

            if len(response_data) == 1:
                return [cls._parse_response(*response_data)]

            results_list = [cls._parse_response(obj) for obj in response_data]
            return results_list

    @classmethod
    async def get_city_names_with_code(cls, city_code):
        request_url = f"https://autocomplete.travelpayouts.com/places2?term={city_code}&locale=ru&types[]=city"
        async with ClientSession() as session:
            async with session.get(request_url) as request:
                response = await request.json()
                city_dict = response[0]
                in_city = city_dict["cases"]["pr"]
                country = city_dict["country_cases"]["su"]
                return in_city, country
