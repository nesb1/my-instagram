from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter
from final_project.data_access_layer.posts import PostsDAL
from final_project.exceptions import PostsDALError
from final_project.models import InPost, Post, PostResponse
from starlette.responses import JSONResponse

router = APIRouter()


@router.get('/', response_model=List[Post])
async def get_posts(user_id: int) -> Any:
    '''
    Возвращает список постов пользователя
    '''


# in_post: InPost
@router.post('/', status_code=HTTPStatus.CREATED.value, response_model=PostResponse)
async def add_post(user_id: int, post: InPost) -> Any:
    '''
    Отдает задачу на обработку
    '''
    try:
        return PostsDAL.add_post(user_id, post)
    except PostsDALError as e:
        return JSONResponse({'message': str(e)})
