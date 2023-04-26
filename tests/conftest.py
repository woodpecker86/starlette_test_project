import pytest as pytest
from starlette.config import environ
from starlette.testclient import TestClient
from sqlalchemy_utils import database_exists, drop_database

environ['TESTING'] = 'True'

from src import config
from src.main import finance_app


@pytest.fixture(autouse=True, scope="session")
def setup_test_database():
    """
    Create a clean test database every time the tests are run.
    """
    url = str(config.DATABASE_URL)
    assert not database_exists(url), 'Test database already exists. Aborting tests.'
    yield
    drop_database(url)


@pytest.fixture()
def client():
    """
    Make a 'client' fixture available to test cases.
    """
    with TestClient(finance_app) as test_client:
        yield test_client
