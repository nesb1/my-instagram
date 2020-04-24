from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends
from final_project.data_access_layer.auth import check_authorization
from final_project.data_access_layer.posts import PostsDAL
from final_project.database.models import User
from final_project.exceptions import PostsDALError
from final_project.messages import Message
from final_project.models import ErrorMessage, InPost, Post, PostResponse
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/', response_model=List[Post])
async def get_posts(user_id: int) -> Any:
    '''
    Возвращает список постов пользователя
    '''


# in_post: InPost
@router.post(
    '/',
    status_code=HTTPStatus.CREATED.value,
    response_model=PostResponse,
    responses={HTTPStatus.FORBIDDEN.value: {'model': ErrorMessage}},
)
async def add_post(
    user_id: int, post: InPost, authorized_user: User = Depends(check_authorization)
) -> Any:
    '''
    Отдает задачу на обработку
    '''
    try:
        if authorized_user.id != user_id:
            return JSONResponse(
                status_code=HTTPStatus.FORBIDDEN.value,
                content={'message': Message.ACCESS_FORBIDDEN.value},
            )
        return PostsDAL.add_post(user_id, post)
    except PostsDALError as e:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST.value, content={'message': str(e)}
        )
