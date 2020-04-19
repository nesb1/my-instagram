from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from final_project.config import tokens_settings
from final_project.data_access_layer.auth import (
    generate_tokens,
    get_user,
    refresh_tokens,
)
from final_project.database.database import create_session
from final_project.database.models import User
from final_project.exceptions import AuthDALError


@pytest.fixture()
def _mock_utc_now(mocker):
    first = datetime.utcnow()
    second = first + timedelta(seconds=1)
    mocker.patch('final_project.data_access_layer.auth.datetime').utcnow.side_effect = [
        first,
        first,
        second,
        second,
    ]
    # при кодирвоании jwt в поле exp видимо отбрасываются милисекунды, поэтому, чтобы токен был разный,
    # нужно подождат секунду


@pytest.fixture()
async def tokens(username, password):
    return await generate_tokens(username, password)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user')
async def test_get_tokens_with_valid_username_and_password(username, password, tokens):
    assert tokens.refresh_token
    assert tokens.access_token
    assert tokens.token_type == tokens_settings.token_type


@pytest.mark.asyncio
async def test_get_tokens_with_invalid_username_and_password_raises_error(
    username, password
):
    with pytest.raises(AuthDALError):
        await generate_tokens(username, password)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_utc_now')
async def test_get_tokens_generates_new_token_pair_for_new_authorization(
    username, password, tokens
):
    new_pair = await generate_tokens(username, password)
    assert new_pair != tokens


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user')
async def test_get_tokens_save_tokens_to_db(username, password, tokens):
    with create_session() as session:
        user = session.query(User).filter(User.username == username).first()
        assert user.access_token == tokens.access_token.decode()
        assert user.refresh_token == tokens.refresh_token.decode()


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user')
async def test_auth_will_let_enter_authentic_user(username, password, tokens):
    user = await get_user(tokens.access_token.decode())
    assert user


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_utc_now')
async def test_get_tokens_generates_new_token_pair_for_new_authorization_and_old_access_token_will_not_valid(
    username, password, tokens
):
    # старая пара должна быть не валидна, хотя время жизни токена еще не истекло
    await generate_tokens(username, password)
    with pytest.raises(HTTPException):
        await get_user(tokens.access_token.decode())


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_utc_now')
async def test_refresh_tokens_returns_new_tokens_pair(username, password, tokens):
    new_tokens = await refresh_tokens(tokens.refresh_token.decode())
    assert new_tokens != tokens


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_utc_now')
async def test_refresh_tokens_saves_new_tokens_pair_to_db(username, password, tokens):
    new_tokens = await refresh_tokens(tokens.refresh_token.decode())
    with create_session() as session:
        user = session.query(User).filter(User.username == username).first()
        assert user.refresh_token == new_tokens.refresh_token.decode()
        assert user.access_token == new_tokens.access_token.decode()


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user')
async def test_refresh_tokens_with_invalid_refresh_token():
    invalid_token = '123'
    with pytest.raises(AuthDALError):
        await refresh_tokens(invalid_token)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_utc_now')
async def test_refresh_with_old_refresh_token_raises_error(username, password, tokens):
    await refresh_tokens(tokens.refresh_token.decode())
    with pytest.raises(AuthDALError):
        await refresh_tokens(tokens.refresh_token.decode())


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user')
async def test_generate_tokens_with_invalid_password(username):
    with pytest.raises(AuthDALError):
        await generate_tokens(username, '2')
