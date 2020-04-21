from http import HTTPStatus
from typing import Any

from fastapi import APIRouter
from final_project.models import Comment, Post

router = APIRouter()


@router.get('/', response_model=Post)
async def get_post(user_id: int, post_id: int) -> Any:
    '''
    Возвращает запись
    '''


@router.post('/likes', response_model=Post, status_code=HTTPStatus.CREATED.value)
async def like(user_id: int, post_id: int) -> Any:
    '''
    Ставит лайк, возвращает статус
    '''


@router.delete('/like', status_code=HTTPStatus.NO_CONTENT.value)
async def remove_like(user_id: int, post_id: int) -> Any:
    '''
    Убирает лайк
    '''


@router.post('/comments', status_code=HTTPStatus.CREATED.value, response_model=Comment)
async def add_comment(user_id: int, post_id: int) -> Any:
    '''
    Добавляет комментарий
    '''


@router.delete('/comments/{comment_id}', status_code=HTTPStatus.NO_CONTENT.value)
async def delete_comment(user_id: int, post_id: int) -> Any:
    '''
    Удаляет комментарий
    '''


@router.post('/comments/{comment_id}/likes', status_code=HTTPStatus.CREATED.value)
async def like_comment(user_id: int, post_id: int) -> Any:
    '''
    Ставит лайк комментарию
    '''


@router.delete('/comments/{comment_id}/like', status_code=HTTPStatus.NO_CONTENT.value)
async def like_comment(user_id: int, post_id: int) -> Any:
    '''
    Убирает лайк с комментария
    '''
