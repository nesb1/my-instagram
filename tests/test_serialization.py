import pytest
from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session
from final_project.database.models import User


@pytest.mark.usefixtures('_init_db', '_add_user')
def test_serialize_user(username):
    with create_session() as session:
        user = session.query(User).filter(User.id == 1).one()
        res = serialize(user)
        assert res.subscriptions == []
        assert res.subscribers == []
        assert res.id == 1
        assert res.username == username


@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_second_user', '_subscribe_on_user'
)
def test_serialize_user_with_subscriber(username, out_user_first):
    with create_session() as session:
        user = session.query(User).filter(User.id == 2).one()
        res = serialize(user)
        assert res.subscribers == [out_user_first]


@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_second_user', '_subscribe_on_user'
)
def test_serialize_user_with_subscriptions(username, out_user_second):
    with create_session() as session:
        user = session.query(User).filter(User.id == 1).one()
        res = serialize(user)
        assert res.subscriptions == [out_user_second]
