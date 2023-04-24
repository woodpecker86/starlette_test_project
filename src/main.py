import contextlib
from datetime import datetime

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import utils
from .config import DEBUG
from .database import connect_to_database, disconnect_from_database
from .crud import get_date_rate


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    await connect_to_database()
    yield
    await disconnect_from_database()


async def start_page(receive: Request) -> JSONResponse:
    rates = await get_date_rate(datetime.now())
    return JSONResponse({'Currencies': rates})


async def get_day_currency(receive: Request) -> JSONResponse:
    needed_day = receive.path_params['day']
    rates = await get_date_rate(needed_day)
    return JSONResponse({'Currencies': rates})


async def get_currency_codes(receive: Request) -> JSONResponse:
    return JSONResponse({'currencies': {'USD': 'Доллар'}})


async def get_currency_rates(receive: Request) -> JSONResponse:
    return JSONResponse({'rates': {'date': 'yyyy-mm-dd',
                                   'char_code': 'USD',
                                   'value': f'{1} to {80}'}})


async def delete_currency(receive: Request) -> JSONResponse:
    return JSONResponse({'Deleted currency': receive.path_params['currency_code']})

routes = [
    Route('/', start_page),
    Route('/currencies', get_currency_codes),
    Route('/rates', get_currency_rates),
    Route('/delete/{currency_code:str}', delete_currency),
    Route('/{day:datetime}', get_day_currency),
]


finance_app = Starlette(debug=DEBUG, routes=routes, lifespan=lifespan)
