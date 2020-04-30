import pathlib

import psycopg2
import pytest
import testing.postgresql
from final_project.app_creation import get_app
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database import database
from final_project.models import InPost, InUser, OutUser
from final_project.redis import RedisInstances
from mock import AsyncMock
from PIL.Image import open as open_to_image
from redis import Redis
from sqlalchemy import create_engine
from starlette.testclient import TestClient


@pytest.fixture()
def client():
    return TestClient(get_app())


@pytest.fixture(scope='session')
def postgres():
    return testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


@pytest.fixture()
def _init_db(postgres):
    ps = postgres()
    database.engine = create_engine(ps.url())
    psycopg2.connect(**ps.dsn())
    database.Base.metadata.create_all(database.engine)
    yield
    database.Base.metadata.drop_all(database.engine)


@pytest.fixture()
def username():
    return 'username'


@pytest.fixture()
def password():
    return 'password'


@pytest.fixture()
def in_user(username, password):
    return InUser(username=username, password=password)


@pytest.fixture()
def second_in_user():
    return InUser(username='user2', password='password')


@pytest.fixture()
async def _add_second_user(second_in_user):
    return await UsersDataAccessLayer.add_user(second_in_user)


@pytest.fixture()
async def _add_user(in_user: InUser):
    await UsersDataAccessLayer.add_user(in_user)


@pytest.fixture()
def resource_directory():
    return pathlib.Path(__file__).resolve().parent / 'images'


@pytest.fixture()
def image(request, resource_directory):
    return open_to_image((resource_directory / request.param).resolve())


@pytest.fixture()
def image_in_bytes(request, resource_directory: pathlib.Path):
    with (resource_directory / request.param).open('rb') as f:
        return f.read()


@pytest.fixture()
def image_2x2_in_bytes(resource_directory):
    with (resource_directory / '2x2.png').open('rb') as f:
        return f.read()


@pytest.fixture()
def image_2x2(resource_directory):
    return open_to_image(resource_directory / '2x2.png')


@pytest.fixture()
def image_1x1(resource_directory):
    return open_to_image(resource_directory / '1x1.png')


@pytest.fixture()
def _mock_sync_redis(mocker):
    mocker.patch.object(Redis, 'sadd')
    mocker.patch.object(Redis, 'hmset')
    mocker.patch.object(Redis, 'hmget')
    mocker.patch.object(Redis, 'srem')


@pytest.fixture()
def _mock_async_redis(mocker):
    mock = mocker.patch.object(RedisInstances, 'async_redis')
    RedisInstances.async_redis = AsyncMock()
    mock.sadd = AsyncMock()
    mock.hmset = AsyncMock()
    mock.hmget = AsyncMock()
    mock.srem = AsyncMock()


@pytest.fixture()
def in_post():
    return InPost(image='1234', description='descr')


@pytest.fixture()
def uuid():
    return 'uuid'


@pytest.fixture()
def out_user_first(in_user):
    return OutUser(id=1, username=in_user.username)


@pytest.fixture()
def out_user_second(second_in_user):
    return OutUser(id=2, username=second_in_user.username)
