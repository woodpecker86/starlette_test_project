import logging

import databases
import sqlalchemy

from .config import DATABASE_URL

logger = logging.getLogger(__name__)

metadata = sqlalchemy.MetaData()


async def get_database():
    return databases.Database(DATABASE_URL)
