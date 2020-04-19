import pytest
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import Base, engine
from final_project.main import app
from final_project.models import InUser
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
