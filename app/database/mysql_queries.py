CLOSEST_AIRPORTS_QUERY = """
SELECT
    name_en, city_code, lat, lon
FROM airports
WHERE ABS(lat - %s) <= %s / 111
AND ABS(lon - %s) <= %s / (111 * COS(radians(%s)));
"""

CITY_AIRPORTS_QUERY = """
SELECT
    name_en, city_code, lat, lon, city_id, country_id
FROM airports
WHERE city_code = %s;
"""

CITY_BY_NAME_QUERY = """
SELECT
    city_name_eng, city_code, country_code
FROM cities
WHERE city_name_eng = %s;
"""

USER_CITY_QUERY = """
SELECT
    c.city_name_eng, c.city_code, c.country_code, c.lat, c.lon
FROM users u
JOIN cities c ON u.city_id = c.id
WHERE u.user_id = %s;
"""

CITY_BY_CODE_QUERY = """
SELECT
    city_name_eng, city_code, country_code, lat, lon
FROM cities WHERE city_code = %s;
"""

USER_UPDATE_OR_CREATE_QUERY = """
INSERT INTO users
    (user_id, username, chat_id, city_id)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE city_id = %s;
"""

USER_SUBSCRIPTIONS_QUERY = """
SELECT
    departure_city_code, arrival_city_code
FROM subscriptions
WHERE user_id = %s;
"""

CREATE_SUBSCRIPTION_QUERY = """
INSERT INTO subscriptions
    (user_id, departure_city_code, arrival_city_code)
VALUES (%s, %s, %s);
"""

DELETE_SUBSCRIPTION_QUERY = """
DELETE FROM subscriptions
WHERE user_id = %s
AND departure_city_code = %s
AND arrival_city_code = %s;
"""

GET_SEASON_CITIES_QUERY = """
SELECT
    c.city_code, c.city_name_ru, c.lat, c.lon
FROM seasons s
JOIN cities c ON s.country_id = c.country_id
"""
