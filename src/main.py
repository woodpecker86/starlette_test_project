import contextlib
from datetime import datetime

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import utils
from .config import DEBUG
from .database import connect_to_database, disconnect_from_database
from .crud import (get_date_rates,
                   get_currencies,
                   delete_currency_data,
                   get_all_rates)


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    await connect_to_database()
    yield
    await disconnect_from_database()


async def start_page(receive: Request) -> JSONResponse:
    rates = await get_date_rates(datetime.now())
    return JSONResponse({'date': datetime.now().strftime('%Y-%m-%d'),
                         'currencies': rates})


async def get_day_currency(receive: Request) -> JSONResponse:
    needed_day = receive.path_params['day']
    rates = await get_date_rates(needed_day)
    return JSONResponse({'date': needed_day.strftime('%Y-%m-%d'),
                         'currencies': rates})


async def get_currency_codes(receive: Request) -> JSONResponse:
    codes = await get_currencies()
    return JSONResponse({'currencies': codes})


async def get_currency_rates(receive: Request) -> JSONResponse:
    limit = int(receive.query_params['limit']) if 'limit' in receive.query_params else 0
    offset = int(receive.query_params['offset']) if 'offset' in receive.query_params else 0
    result = await get_all_rates(limit, offset)
    return JSONResponse({'rates': result})


async def delete_currency(receive: Request) -> JSONResponse:
    try:
        char_code = receive.query_params['char_code']
    except KeyError:
        return JSONResponse({'Status': 'error',
                             'Msg': 'not specified currency char_code'})
    rows_num = await delete_currency_data(char_code)
    return JSONResponse({'Status': 'ok',
                        'Number of deleted rates': rows_num})


routes = [
    Route('/', start_page),
    Route('/currencies', get_currency_codes),
    Route('/rates', get_currency_rates),
    Route('/delete', delete_currency),
    Route('/{day:datetime}', get_day_currency),
]


finance_app = Starlette(debug=DEBUG, routes=routes, lifespan=lifespan)
