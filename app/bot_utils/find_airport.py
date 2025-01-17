import asyncio

from geopy.distance import geodesic

from database.db_api import DatabaseQueries


class AirportFinder:
    @classmethod
    async def find_nearest_airport(cls, user_coordinates):
        nearest_airport = None
        nearest_city_code = None
        min_distance = float("inf")
        airports_coords = await asyncio.create_task(DatabaseQueries.get_airports_coordinates())

        for airport_name, city_code, latitude, longitude in airports_coords:
            airport_coordinates = (latitude, longitude)
            distance = geodesic(user_coordinates, airport_coordinates).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest_airport = airport_name
                nearest_city_code = city_code
        return nearest_airport, nearest_city_code
