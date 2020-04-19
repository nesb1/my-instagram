from http import HTTPStatus

import pytest
from final_project.exceptions import AuthDALError
from final_project.messages import Message
from final_project.models import TokensResponse
from mock import AsyncMock


@pytest.fixture()
def mocked_auth(mocker):
    mock = mocker.patch('final_project.api.auth.auth')
    mock.refresh_tokens = AsyncMock()
    mock.generate_tokens = AsyncMock()
    return mock


@pytest.fixture()
def refresh_token_payload():
    return {'token': '12345'}


@pytest.fixture()
def tokens_for_test():
    access_token = b'123'
    refresh_token = b'1234'
    return TokensResponse(
        token_type='bearer', access_token=access_token, refresh_token=refresh_token
    )


def test_refresh_toke_returns_expected_value(
    mocked_auth, client, refresh_token_payload, tokens_for_test
):
    mocked_auth.refresh_tokens.return_value = tokens_for_test
    response = client.post('/auth/fresh_token', json=refresh_token_payload)
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 3
    assert json['access_token'] == tokens_for_test.access_token.decode()
    assert json['refresh_token'] == tokens_for_test.refresh_token.decode()


def test_refresh_token_with_error_returns_expected_value(
    mocked_auth, client, refresh_token_payload
):
    mocked_auth.refresh_tokens.side_effect = AuthDALError(
        Message.INVALID_REFRESH_TOKEN.value
    )
    response = client.post('/auth/fresh_token', json=refresh_token_payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    json = response.json()
    assert len(json) == 1
    assert json['message'] == Message.INVALID_REFRESH_TOKEN.value


@pytest.fixture()
def auth_data():
    return {'grant_type': 'password', 'username': '1', 'password': '1'}


def test_login_returns_expected_value(mocked_auth, client, tokens_for_test, auth_data):
    mocked_auth.generate_tokens.return_value = tokens_for_test
    response = client.post('/auth/token', data=auth_data)
    json = response.json()
    assert response.status_code == HTTPStatus.OK
    assert len(json) == 3
    assert json['access_token'] == tokens_for_test.access_token.decode()
    assert json['refresh_token'] == tokens_for_test.refresh_token.decode()


def test_login_returns_expected_error(mocked_auth, client, auth_data):
    mocked_auth.generate_tokens.side_effect = AuthDALError(
        Message.INCORRECT_USERNAME_OR_PASSWORD.value
    )
    response = client.post('/auth/token', data=auth_data)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    json = response.json()
    assert len(json) == 1
    assert json['message'] == Message.INCORRECT_USERNAME_OR_PASSWORD.value
