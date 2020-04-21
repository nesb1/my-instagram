from copy import deepcopy
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Awaitable, Dict, Optional, Union

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from final_project.config import tokens_settings
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import create_session, run_in_threadpool
from final_project.database.models import User
from final_project.exceptions import AuthDALError
from final_project.messages import Message
from final_project.models import TokensResponse
from final_project.password import get_password_hash
from jwt import PyJWTError
from starlette.responses import JSONResponse

SECRET_KEY = '123'
ALGORITHM = 'HS256'
TOKEN_TYPE = 'bearer'
oauth_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


async def _get_user_from_db(user_id: int) -> User:
    user = await UsersDataAccessLayer.get_user(user_id, without_error=True)
    if not user:
        raise AuthDALError(Message.USER_DOES_NOT_EXISTS.value)
    return user


def _get_user_id(token: str) -> int:
    try:
        payload: Dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('sub')
        if not user_id or not isinstance(user_id, int):
            raise AuthDALError(Message.NOT_EXPECTING_PAYLOAD.value)
        return user_id
    except PyJWTError:
        raise AuthDALError(Message.COULD_NOT_VALIDATE_CREDENTIALS.value)


def _is_valid_token(actual_token: str, expected_token: str) -> bool:
    return actual_token == expected_token


async def check_authorization(
    token: str = Depends(oauth_scheme),
) -> Union[User, JSONResponse]:
    '''
    Обрабатывает jwt
    :raises HttpException со статусом 401 если произошла ошибка при обработке токена
    :return: user
    '''
    try:
        user_id = _get_user_id(token)
        user = await _get_user_from_db(user_id)
        if _is_valid_token(token, user.access_token):
            return user
        raise AuthDALError(Message.ACCESS_TOKEN_OUTDATED.value)
    except AuthDALError as e:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            headers={'WWW-Authenticate': 'Bearer'},
            content={'message': str(e)},
        )


def _is_password_correct(password: str, expected_password_hash: str) -> bool:
    return get_password_hash(password) == expected_password_hash


@run_in_threadpool
def _authenticate_user(username: str, password: str) -> Awaitable[User]:
    message = Message.INCORRECT_USERNAME_OR_PASSWORD.value
    with create_session() as session:
        user: Optional[User] = session.query(User).filter(
            User.username == username
        ).first()
        user = deepcopy(user)
    if user is None:
        raise AuthDALError(message)
    if _is_password_correct(password, user.password_hash):
        return user
    raise AuthDALError(message)


def _create_token(user_id: int, expires_delta: timedelta) -> bytes:
    expires_in = datetime.utcnow() + expires_delta
    payload: Dict[str, Any] = {'sub': user_id, 'exp': expires_in}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@run_in_threadpool
def _save_tokens_to_db(user: User, access_token: bytes, refresh_token: bytes) -> None:
    user.access_token = access_token.decode()
    user.refresh_token = refresh_token.decode()
    with create_session() as session:
        session.add(user)


async def _create_tokens(user: User) -> TokensResponse:
    access_token = _create_token(
        user.id, timedelta(minutes=tokens_settings.access_token_expire_minutes)
    )
    refresh_token = _create_token(
        user.id, timedelta(days=tokens_settings.refresh_toke_expire_time_days)
    )
    await _save_tokens_to_db(user, access_token, refresh_token)
    return TokensResponse(
        access_token=access_token, refresh_token=refresh_token, token_type=TOKEN_TYPE
    )


async def generate_tokens(username: str, password: str) -> TokensResponse:
    '''
    Создает access и refresh токены
    '''
    user = await _authenticate_user(username, password)
    return await _create_tokens(user)


async def refresh_tokens(refresh_token: str) -> TokensResponse:
    '''
    Проверяет refresh_token и возвращает новую пару токенов
    '''
    user_id = _get_user_id(refresh_token)
    user = await _get_user_from_db(user_id)
    if not _is_valid_token(refresh_token, user.refresh_token):
        raise AuthDALError(Message.INVALID_REFRESH_TOKEN.value)
    return await _create_tokens(user)
