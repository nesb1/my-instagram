from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter
from final_project.models import InPost, Post

router = APIRouter()


@router.get('/', response_model=List[Post])
async def get_posts(user_id: int) -> Any:
    '''
    Возвращает список постов пользователя
    '''


@router.post('/', response_model=Post, status_code=HTTPStatus.CREATED.value)
async def add_post(user_id: int, in_post: InPost) -> Any:
    '''
    Возвращает запись, которая была создана
    '''
