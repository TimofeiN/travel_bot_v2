import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
AVIASALES_TOKEN = os.environ.get("AVIASALES_TOKEN")
OPEN_WEATHER_TOKEN = os.environ.get("OPEN_WEATHER_TOKEN")

MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

DB_HOST = os.environ.get("DB_HOST", "bot-db")
DB_PORT = os.environ.get("DB_PORT", 3306)

MYSQL_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "db": MYSQL_DATABASE,
}
