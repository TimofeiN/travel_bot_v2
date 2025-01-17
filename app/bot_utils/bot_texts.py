from enum import Enum


class StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class AnswerText(StringEnum):
    CHEAPEST = "The cheapest tickets:"
    YOU_CAN_FLY = "You can fly to {destination} for {price} RUB.\n {weather}"
    SUBSCRIBE = "You have successfully subscribed!"
    NO_TICKETS = "No tickets available for the selected destination."

    DESTINATION = "Choose a destination:"
    LIMIT = "How many search results to show?\n From 1 to 10."
    WRONG_LIMIT = "Please enter a number between 1 and 10."

    START = "Hello, {username}"
    CITY_OR_LOCATION = (
        "Enter the name of the city you want to depart from, or provide access to "
        "your geolocation, and we will find the nearest airport."
    )
    HELP_COMMAND = "Someday, there will be a description of how the bot works here."

    LOCATION = "The nearest airport to you is {airport} in {in_city} ({country})."
    LOCATION_MANY = (
        "The nearest airport to you is {airport} in {in_city} ({country}).\n"
        "This city also has other airports: {airports}"
    )
    ENTER_CITY = 'Enter the name of the city or press the "Request geolocation" button.'
    CITY_WITH_AIRPORT_NOT_FOUND = "No city with an airport found."
    CITY_FOUND = "The selected departure city is {city_name} with the airport {airport_name}."
    CITIES_FOUND = "The selected departure city is {city_name} with the airports {airports_names}."
    TWO_CITIES = "Two cities with this name were found."

    WEATHER = "Enter the city:"
    WEATHER_IN_YOUR_CITY = "{result}."
    WEATHER_IN_ANY_CITY = "{result}."
    WEATHER_ACTION = "Where would you like to check the weather?"
    WEATHER_WRONG_CITY = "No data is available for the city {city}. Check the name or enter another city."

    ACTIONS = "Choose an action:"
    SEASON = "You can fly during the summer season:"
    SEASON_WEATHER = "You can fly to {destination} for {price}\n {weather}"

    SUBSCRIPTIONS = "Your subscriptions:\n"
    SUBSCRIPTION = "From {origin} to {arrival}"
    UNSUBSCRIPTION = "Subscription canceled."
    NO_SUBSCRIPTIONS = "You have no subscriptions."


class ButtonText(StringEnum):
    BUY = "Buy"
    SUBSCRIBE = "Subscribe"
    SUBSCRIPTIONS = "Your subscriptions"
    FIVE_CHEAPEST = "The cheapest tickets"
    SEASON = "Season"
    WEATHER = "Weather"
    WEATHER_IN_YOUR_CITY = "Weather in the departure city"
    WEATHER_IN_ANY_CITY = "Weather in any city"
    LOCATION = "Request geolocation"
    UNSUBSCRIBE = "Cancel subscription"
