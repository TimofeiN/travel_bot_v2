import logging
from contextlib import asynccontextmanager

import aiomysql
import pymysql

from config import settings

log = logging.getLogger(__name__)


@asynccontextmanager
async def mysql_cursor(autocommit: bool = True) -> None:
    try:
        async with aiomysql.connect(**settings.MYSQL_CONFIG, autocommit=autocommit) as connection:
            async with connection.cursor() as cursor:
                yield cursor
    except pymysql.MySQLError as db_error:
        log.error("MySQL error: %s", db_error, exc_info=True)
        raise
