import databases
from starlette.config import Config


config = Config('.env')

DEBUG = config('DEBUG', cast=bool, default=False)
TESTING = config('TESTING', cast=bool, default=False)

DATABASE_URL = config('DATABASE_URL', cast=databases.DatabaseURL)
if TESTING:
    DATABASE_URL = DATABASE_URL.replace(database='test_' + DATABASE_URL.database)
