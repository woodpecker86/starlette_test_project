from starlette.config import Config


config = Config('.env')

DEBUG = config('DEBUG', cast=bool, default=False)
TESTING = config('TESTING', cast=bool, default=False)

CURRENCY_RATE_SOURCE = config('CURRENCY_RATE_SOURCE')

DATABASE_URL = config('DATABASE_URL')
if TESTING:
    DATABASE_URL = 'test_' + DATABASE_URL
