import pathlib

import pytest
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import Base, engine
from final_project.main import app
from final_project.models import InUser
from PIL.Image import open as open_to_image
from starlette.testclient import TestClient


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def _init_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


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
async def _add_user(in_user: InUser):
    await UsersDataAccessLayer.add_user(in_user)


@pytest.fixture()
def resource_directory():
    return pathlib.Path(__file__).resolve().parent / 'images'


@pytest.fixture()
def image(request, resource_directory):
    return open_to_image((resource_directory / request.param).resolve())
