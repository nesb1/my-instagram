from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends
from final_project.data_access_layer.auth import check_authorization
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.exceptions import UsersDALDoesNotExistsError, UsersDALError
from final_project.messages import Message
from final_project.models import (
    ErrorMessage,
    InUser,
    OutUser,
    PostWithImage,
    UserId,
    UserInDetailOut,
)
from starlette.responses import JSONResponse

router = APIRouter()

forbidden_json_response = JSONResponse(
    {'message': str(Message.ACCESS_FORBIDDEN.value)},
    status_code=HTTPStatus.FORBIDDEN.value,
)


@router.post(
    '/',
    response_model=OutUser,
    responses={HTTPStatus.BAD_REQUEST.value: {'model': ErrorMessage}},
    status_code=HTTPStatus.CREATED.value,
)
async def register_user(user: InUser) -> Any:
    """
    Регистрация пользователя
    """
    try:
        return await UsersDataAccessLayer.add_user(user)
    except UsersDALError as e:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST.value, content={'message': str(e)}
        )


@router.post(
    '/{user_id}/subscriptions/',
    status_code=HTTPStatus.CREATED.value,
    response_model=List[OutUser],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
)
async def subscribe(
    user_id: int, another_user: UserId, user: OutUser = Depends(check_authorization)
) -> Any:
    '''
    Возвращает список подписок
    '''
    try:
        if user_id != user.id:
            return JSONResponse(
                {'message': str(Message.ACCESS_FORBIDDEN.value)},
                status_code=HTTPStatus.FORBIDDEN.value,
            )
        return await UsersDataAccessLayer.subscribe(
            user_id=user.id, want_subscribe_on_user_with_id=another_user.user_id
        )
    except UsersDALDoesNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)
    except UsersDALError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.BAD_REQUEST.value)


@router.delete(
    '/{user_id}/subscriptions/{another_user_id}/',
    dependencies=[Depends(check_authorization)],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
    status_code=HTTPStatus.NO_CONTENT.value,
)
async def unsubscribe(
    user_id: int, another_user: UserId, user: OutUser = Depends(check_authorization)
) -> Any:
    try:
        if user_id != user.id:
            return forbidden_json_response
        return await UsersDataAccessLayer.unsubscribe(
            user_id=user.id, want_unsubscribe_on_user_with_id=another_user.user_id
        )
    except UsersDALDoesNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)
    except UsersDALError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.BAD_REQUEST.value)


@router.get(
    '/',
    dependencies=[Depends(check_authorization)],
    response_model=List[UserInDetailOut],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
)
async def search(substring: str) -> Any:
    '''
    Исчет пользователей в системе по логину и возвращает возможных
    '''
    return await UsersDataAccessLayer.get_users_by_substring_in_username(substring)


@router.get(
    '/{user_id}',
    dependencies=[Depends(check_authorization)],
    response_model=UserInDetailOut,
)
async def get_user_by_id(user_id: int) -> Any:
    try:
        return await UsersDataAccessLayer.get_user_by_id(user_id)
    except UsersDALDoesNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


@router.get('{user_id}/feed', response_model=List[PostWithImage])
async def get_feed(
    user_id: int, page: int, size: int, user: OutUser = Depends(check_authorization)
) -> Any:
    try:
        if user_id != user.id:
            return forbidden_json_response
        return await UsersDataAccessLayer.get_feed(
            user_id=user_id, page=page, size=size
        )
    except UsersDALDoesNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)
    except UsersDALError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.BAD_REQUEST.value)
