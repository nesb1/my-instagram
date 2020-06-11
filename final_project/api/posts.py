from http import HTTPStatus
from typing import List, Union

from fastapi import APIRouter, Depends
from final_project.api.utils import check_user
from final_project.data_access_layer.auth import check_authorization
from final_project.data_access_layer.posts import PostsDAL
from final_project.database.models import User
from final_project.models import InPost, PostWithImage, TaskResponse
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/', response_model=List[PostWithImage])
async def get_posts(user_id: int) -> List[PostWithImage]:
    return await PostsDAL.get_posts(user_id)


@router.post(
    '/', status_code=HTTPStatus.CREATED.value,
)
async def add_post(
    user_id: int, post: InPost, authorized_user: User = Depends(check_authorization)
) -> Union[JSONResponse, TaskResponse]:
    '''
    Отдает задачу на обработку
    '''
    check_user(user_id, authorized_user.id)
    return await PostsDAL.add_post(user_id, post)


@router.get('/task/{task_id}/', response_model=TaskResponse)
async def get_task_status(
    user_id: int, task_id: str, authorized_user: User = Depends(check_authorization)
) -> TaskResponse:
    check_user(user_id, authorized_user.id)
    return await PostsDAL.get_task_status(task_id)
