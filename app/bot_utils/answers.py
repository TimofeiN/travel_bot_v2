from dataclasses import dataclass


@dataclass(frozen=True)
class Answers:
    cheapest = "Самые дешёвые билеты:"
    you_can_fly: str = "Вы можете улететь в город {destination} за {price} р.\n {weather}"
    subscribe: str = "Вы успешно подписаны!"
    no_tickets: str = "Нет билетов по заданному направлению."

    destination: str = "Выберите направление: "
    limit: str = "Сколько результатов поиска показать?\n От 1 до 10."
    wrong_limit: str = "Введите число от 1 до 10"

    start: str = "Здравствуйте, {username}"
    city_or_location: str = (
        "Напишите название города из которого Вы хотели бы вылетать или предоставьте доступ к "
        "геолокации и мы найдём ближайший аэропорт."
    )
    help_command: str = "Когда-нибудь здесь будет описание работы бота"

    location: str = "Ближайший к Вам аэропорт - {airport} в {in_city} ({country})."
    location_many: str = (
        "Ближайший к Вам аэропорт - {airport} в {in_city} ({country}).\n" "В этом городе ещё есть аэропорты: {airports}"
    )
    enter_city: str = 'Введите название города или нажмите кнопку "Запрос геолокации"'
    city_with_airport_not_found: str = "Такой город с аэропортом не найден."
    city_found = "В качестве города отправления выбран {city_name} c аэропортом {airport_name}"
    cities_found = "В качестве города отправления выбран {city_name} c аэропортами {airports_names}"
    two_cities = "Найдено два города с таким названием"

    weather: str = "Введите город:"
    weather_in_your_city: str = "{result}."
    weather_in_any_city: str = "{result}."
    weather_action: str = "Где Вы хотите узнать погоду?"
    weather_wrong_city: str = "Для города {city} нет данных. Проверьте название или введите другой город."

    actions: str = "Выберите действие:"
    season: str = "Mожно улететь в летний сезон:"
    season_weather: str = "Вы можете улететь в {destination} за {price}\n {weather}"

    subscriptions = "Ваши подписки:\n"
    subscription = "Из города {origin} в город {arrival}"
    unsubscription = "Подписка отменена"
    no_subscriptions = "У вас нет подписок"


answers = Answers()
