import contextlib

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import utils
from .config import DEBUG
from .database import connect_to_database, disconnect_from_database


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    await connect_to_database()
    yield
    await disconnect_from_database()


async def start_page(receive: Request) -> JSONResponse:
    return JSONResponse({'hello': 'world'})


async def get_day_currency(receive: Request) -> JSONResponse:
    needed_day = receive.path_params['day']
    return JSONResponse({'day': 'ddd'})


async def get_currency_codes(receive: Request) -> JSONResponse:
    return JSONResponse({'currencies': ['USD']})


async def delete_currency(receive: Request) -> JSONResponse:
    return JSONResponse({'Deleted currency': receive.path_params['currency_code']})

routes = [
    Route('/', start_page),
    Route('/currencies', get_currency_codes),
    Route('/delete/{currency_code:str}', delete_currency),
    Route('/{day:datetime}', get_day_currency),
]


finance_app = Starlette(debug=DEBUG, routes=routes, lifespan=lifespan)
