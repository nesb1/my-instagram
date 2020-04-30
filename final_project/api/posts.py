from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends
from final_project.data_access_layer.auth import check_authorization
from final_project.data_access_layer.posts import PostsDAL
from final_project.database.models import User
from final_project.exceptions import PostsDALError, PostsDALNotExistsError
from final_project.messages import Message
from final_project.models import InPost, PostWithImage, TaskResponse
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/', response_model=List[PostWithImage])
async def get_posts(user_id: int) -> Any:
    try:
        return await PostsDAL.get_posts(user_id)
    except PostsDALError as e:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST.value, content={'message': str(e)}
        )
    except PostsDALNotExistsError as e:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND.value, content={'message': str(e)}
        )


@router.post(
    '/', status_code=HTTPStatus.CREATED.value,
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
        return await PostsDAL.add_post(user_id, post)
    except PostsDALError as e:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST.value, content={'message': str(e)}
        )
    except PostsDALNotExistsError as e:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND.value, content={'message': str(e)}
        )


@router.get('/task/{task_id}/', response_model=TaskResponse)
async def get_task_status(task_id: str) -> Any:
    try:
        return await PostsDAL.get_task_status(task_id)
    except PostsDALNotExistsError as e:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND.value, content={'message': str(e)}
        )
