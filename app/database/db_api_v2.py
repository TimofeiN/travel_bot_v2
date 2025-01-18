from datetime import datetime
from enum import Enum
from typing import Final, Optional

from .models import Airport, City, Subscription
from .mysql_cursor import mysql_cursor
from .mysql_queries import (
    CITY_AIRPORTS_QUERY,
    CITY_BY_CODE_QUERY,
    CITY_BY_NAME_QUERY,
    CLOSEST_AIRPORTS_QUERY,
    CREATE_SUBSCRIPTION_QUERY,
    DELETE_SUBSCRIPTION_QUERY,
    GET_SEASON_CITIES_QUERY,
    USER_CITY_QUERY,
    USER_SUBSCRIPTIONS_QUERY,
    USER_UPDATE_OR_CREATE_QUERY,
)

DISTANCE_KM: Final[int] = 500
SUMMER_SEASON: Final[str] = "S"


class UpdateOrCreateResult(Enum):
    CREATED = 1
    UPDATED = 2


class DatabaseAPI:
    @staticmethod
    async def get_closest_airports(user_lat, user_lon) -> Optional[list[Airport]]:
        async with mysql_cursor() as cursor:
            await cursor.execute(
                query=CLOSEST_AIRPORTS_QUERY, args=[user_lat, DISTANCE_KM, user_lon, DISTANCE_KM, user_lat]
            )
            fetched_data = await cursor.fetchall()
            if not fetched_data:
                return None

        return [Airport(*row) for row in fetched_data]

    @staticmethod
    async def get_city_airports(city_code: str) -> Optional[list[Airport]]:
        async with mysql_cursor() as cursor:
            await cursor.execute(query=CITY_AIRPORTS_QUERY, args=[city_code])
            fetched_data = await cursor.fetchall()
            if not fetched_data:
                return None

        return [Airport(*row) for row in fetched_data]

    @staticmethod
    async def get_cities_by_name(city_name: str) -> Optional[list[City]]:
        async with mysql_cursor() as cursor:
            await cursor.execute(query=CITY_BY_NAME_QUERY, args=[city_name])
            fetched_data = await cursor.fetchall()
            if not fetched_data:
                return None

        return [City(*row) for row in fetched_data]

    @staticmethod
    async def get_user_city(user_id) -> Optional[City]:
        async with mysql_cursor() as cursor:
            await cursor.execute(query=USER_CITY_QUERY, args=[user_id])
            fetched_data = await cursor.fetchone()

        city = City(*fetched_data) if fetched_data else None
        return city

    @staticmethod
    async def get_city_by_code(city_code: str) -> Optional[City]:
        async with mysql_cursor() as cursor:
            await cursor.execute(query=CITY_BY_CODE_QUERY, args=[city_code])
            fetched_data = await cursor.fetchone()

        city = City(*fetched_data) if fetched_data else None
        return city

    @staticmethod
    async def user_update_or_create(user_id, username, chat_id, city_id) -> Optional[UpdateOrCreateResult]:
        async with mysql_cursor() as cursor:
            query_result = await cursor.execute(
                query=USER_UPDATE_OR_CREATE_QUERY, args=[user_id, username, chat_id, city_id, city_id]
            )
            if not query_result:
                return None

        return UpdateOrCreateResult(query_result)

    @staticmethod
    async def get_user_subscriptions(user_id: int) -> Optional[list[Subscription]]:
        async with mysql_cursor() as cursor:
            await cursor.execute(query=USER_SUBSCRIPTIONS_QUERY, args=[user_id])
            fetched_data = await cursor.fetchall()
            if not fetched_data:
                return None

        return [Subscription(*row) for row in fetched_data if row]

    @staticmethod
    async def create_subscription(user_id: int, origin_code: str, destination_code: str) -> UpdateOrCreateResult:
        async with mysql_cursor() as cursor:
            query_result = await cursor.execute(
                query=CREATE_SUBSCRIPTION_QUERY, args=[user_id, origin_code, destination_code]
            )
        return UpdateOrCreateResult(query_result)

    @staticmethod
    async def delete_subscription(user_id: int, origin_code: str, destination_code: str) -> list[Subscription]:
        async with mysql_cursor() as cursor:
            query_result = await cursor.execute(
                query=DELETE_SUBSCRIPTION_QUERY, args=[user_id, origin_code, destination_code]
            )

        return query_result

    @staticmethod
    def _prepare_seasons_query(initial_query: str = GET_SEASON_CITIES_QUERY) -> str:
        query = initial_query
        current_month = datetime.now().month
        month_column = f"s.month_{current_month}"
        query += f"WHERE {month_column} = %s;"
        return query

    @classmethod
    async def get_summer_season_cities(cls) -> Optional[list[City]]:
        query = cls._prepare_seasons_query()

        async with mysql_cursor() as cursor:
            await cursor.execute(query=query, args=[SUMMER_SEASON])
            fetched_data = await cursor.fetchall()
            if not fetched_data:
                return None

        return [City(*row) for row in fetched_data if row]
