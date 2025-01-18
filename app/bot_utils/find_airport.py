from typing import Optional

from geopy.distance import geodesic

from database import Airport, DatabaseAPI


class AirportFinder:
    @classmethod
    async def find_closest_airport(cls, user_coordinates: tuple[float, float]) -> Optional[Airport]:
        closest_airport = None
        min_distance = float("inf")

        closest_airports = await DatabaseAPI.get_closest_airports(*user_coordinates)
        if not closest_airports:
            return None

        for airport in closest_airports:
            airport_coordinates = (airport.latitude, airport.longitude)
            distance = geodesic(user_coordinates, airport_coordinates).kilometers
            if distance > min_distance:
                continue

            min_distance = distance
            closest_airport = airport

        return closest_airport
