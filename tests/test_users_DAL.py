import pytest
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import create_session
from final_project.database.models import User
from final_project.exceptions import UsersDALDoesNotExistsError, UsersDALError
from final_project.password import get_password_hash


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_add_new_user_returns_expected_value(in_user):
    actual = await UsersDataAccessLayer.add_user(in_user)
    assert actual.username == in_user.username
    assert actual.id == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_add_new_user_adds_data_to_database(in_user):
    with create_session() as s:
        user = s.query(User).filter(User.id == 1).first()
        assert user
        assert user.username == in_user.username


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_add_user_that_already_exists_will_raise_error(in_user):
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.add_user(in_user)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_add_user_function_encrypts_password(in_user):
    with create_session() as s:
        user = s.query(User).filter(User.id == 1).first()
        assert user.password_hash == get_password_hash(in_user.password)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_get_existing_user_returns_expected_value(username):
    user = await UsersDataAccessLayer.get_user(1)
    assert user
    assert user.username == username


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_not_existing_user_raises_error():
    with pytest.raises(UsersDALDoesNotExistsError):
        await UsersDataAccessLayer.get_user(1)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_not_existing_user_with_show_error_true_returns_none():
    assert await UsersDataAccessLayer.get_user(1, without_error=True) is None


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_subscribe_on_user_that_does_not_exists_raises_error():
    with pytest.raises(UsersDALDoesNotExistsError):
        await UsersDataAccessLayer.subscribe(1, 2)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_subscribe_on_myself_will_raise_error():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.subscribe(1, 1)


@pytest.fixture()
async def _subscribe_on_user():
    await UsersDataAccessLayer.subscribe(1, 2)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_second_user','_subscribe_on_user')
async def test_subscribe_two_times_will_raises_error():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.subscribe(1, 2)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_second_user')
async def test_subscribe_on_user_returns_expected_value(out_user_second):
    res = await UsersDataAccessLayer.subscribe(1, 2)
    assert len(res) == 1
    assert res[0] == out_user_second


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_second_user')
async def test_subscribe_on_user_change_data_on_db(out_user_first):
    await UsersDataAccessLayer.subscribe(1, 2)
    with create_session() as session:
        user = session.query(User).filter(User.id == 1).one()
        subscriptions = user.subscriptions
        assert len(subscriptions) == 1
        user2: User = session.query(User).filter(User.id == 2).one()
        assert user2 in subscriptions
        subscribers = user2.subscribers
        assert len(subscribers) == 1
        assert user in subscribers


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_second_user', '_subscribe_on_user'
)
async def test_unsubscribe_from_user_returns_expected_value(out_user_second):
    res = await UsersDataAccessLayer.unsubscribe(1, 2)
    assert len(res) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_second_user')
async def test_unsubscribe_from_user_that_not_in_subscriptions():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.unsubscribe(1, 2)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_unsubscribe_from_myself():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.unsubscribe(1, 1)
