from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends
from final_project.data_access_layer.auth import get_user
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.models import User
from final_project.exceptions import UsersDALError
from final_project.models import ErrorMessage, InUser, OutUser
from starlette.responses import JSONResponse

router = APIRouter()


@router.post(
    '/',
    response_model=OutUser,
    responses={HTTPStatus.BAD_REQUEST.value: {'model': ErrorMessage}},
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


@router.get('/', responses={HTTPStatus.UNAUTHORIZED.value : {"model" : ErrorMessage}})
async def k(user: User = Depends(get_user)) -> Any:
    '''
    Функция для ручного теста
    '''
    return user.username
