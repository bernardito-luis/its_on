from typing import Callable, Generator

import pytest
from dynaconf import settings
from its_on.main import init_gunicorn_app
from its_on.models import switches

from .helpers import create_sample_data, create_tables, drop_tables, setup_db, teardown_db


@pytest.fixture
async def client(aiohttp_client: Callable) -> None:
    app = await init_gunicorn_app()
    return await aiohttp_client(app)


@pytest.fixture
async def switch(client):
    async with client.server.app['db'].acquire() as conn:
        result = await conn.execute(switches.select().where(switches.c.id == 1))
        return await result.first()


@pytest.fixture
async def login(client):
    await client.post('/zbs/login', data={'login': 'admin', 'password': 'password'})


@pytest.fixture
async def user_login(client):
    await client.post('/zbs/login', data={'login': 'user1', 'password': 'password'})


@pytest.fixture(scope='session')
def setup_database() -> Generator:
    setup_db(config=settings)
    yield
    teardown_db(config=settings)


@pytest.fixture(scope='function')
def setup_tables(setup_database: Callable) -> Generator:
    create_tables(config=settings)
    yield
    drop_tables(config=settings)


@pytest.fixture(scope='function')
def setup_tables_and_data(setup_tables: Callable) -> Generator:
    create_sample_data(config=settings)
    yield
