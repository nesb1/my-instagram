from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends
from final_project.data_access_layer.auth import check_authorization
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.exceptions import UsersDALError
from final_project.models import ErrorMessage, InUser, OutUser, UserId
from starlette.responses import JSONResponse

router = APIRouter()


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


@router.get(
    '/{user_id}/subscribers/',
    dependencies=[Depends(check_authorization)],
    response_model=List[OutUser],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
)
async def get_subscribers(user_id: int) -> Any:
    '''
    Возвращает список подписчиков
    '''


@router.get(
    '/{user_id}/subscriptions/',
    dependencies=[Depends(check_authorization)],
    response_model=List[OutUser],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
)
async def get_subscriptions(user_id: int) -> Any:
    '''
    Возвращает список подписок
    '''


@router.post(
    '/{user_id}/subscriptions/',
    status_code=HTTPStatus.CREATED.value,
    response_model=List[OutUser],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
)
async def subscribe(
    another_user: UserId, user: OutUser = Depends(check_authorization)
) -> Any:

    '''
    Возвращает список подписок
    '''


@router.delete(
    '/{user_id}/subscriptions/{another_user_id}/',
    dependencies=[Depends(check_authorization)],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
    status_code=HTTPStatus.NO_CONTENT.value,
)
async def unsubscribe(user_id: int, another_user_id: int) -> Any:
    pass


@router.get(
    '/',
    dependencies=[Depends(check_authorization)],
    response_model=List[OutUser],
    responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
)
async def search(substring: str) -> Any:
    '''
    Исчет пользователей в системе по логину и возвращает возможных
    '''
