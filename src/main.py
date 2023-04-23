import contextlib
import logging

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .config import DEBUG
from .database import get_database

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(starlette: Starlette):
    database = await get_database()
    await database.connect()
    yield
    await database.disconnect()


async def homepage(scope, receive, send):
    assert scope['type'] == 'http'
    response = JSONResponse({'hello': 'world'})
    await response(scope, receive, send)


routes = [
    Route('/', homepage),
]

finance_app = Starlette(debug=DEBUG, routes=routes, lifespan=lifespan)
