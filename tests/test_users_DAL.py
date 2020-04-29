import pytest
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import create_session
from final_project.database.models import User
from final_project.exceptions import UsersDALError
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
    assert user.password_hash


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_not_existing_user_raises_error():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.get_user(1)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_not_existing_user_with_show_error_true_returns_none():
    assert await UsersDataAccessLayer.get_user(1, without_error=True) is None
