import pytest
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
