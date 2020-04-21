from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from final_project.data_access_layer import auth
from final_project.exceptions import AuthDALError
from final_project.models import FreshTokenInput, TokensResponse
from starlette.responses import JSONResponse

router = APIRouter()


@router.post(
    '/token', response_model=TokensResponse, status_code=HTTPStatus.CREATED.value
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    '''
    Проверяет есть ли пользователь в системе, возвращает refresh token и access token
    '''
    try:
        res = await auth.generate_tokens(form_data.username, form_data.password)
        return res.__dict__
    except AuthDALError as e:
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED, content={'message': str(e)}
        )


@router.post(
    '/fresh_token', response_model=TokensResponse, status_code=HTTPStatus.CREATED.value
)
async def get_fresh_token(refresh_token: FreshTokenInput) -> Any:
    try:
        return await auth.refresh_tokens(refresh_token.token)
    except AuthDALError as e:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST.value, content={'message': str(e)}
        )
