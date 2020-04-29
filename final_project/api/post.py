from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends
from final_project.data_access_layer.post import PostDAL
from final_project.exceptions import PostDALNotExistsError
from final_project.models import Comment, Post, PostWithImage
from starlette.responses import JSONResponse

router = APIRouter()


class CommonPathParams:
    def __init__(self, user_id: int, post_id: int) -> None:
        self.user_id = user_id
        self.post_id = post_id


@router.get('/', response_model=PostWithImage)
async def get_post(commons: CommonPathParams = Depends(CommonPathParams)) -> Any:
    '''
    Возвращает запись
    '''
    try:
        return await PostDAL.get_post(post_id=commons.post_id)
    except PostDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


@router.post('/likes', response_model=Post, status_code=HTTPStatus.CREATED.value)
async def like(commons: CommonPathParams = Depends(CommonPathParams)) -> Any:
    '''
    Ставит лайк, возвращает статус
    '''


@router.delete('/like', status_code=HTTPStatus.NO_CONTENT.value)
async def remove_like(commons: CommonPathParams = Depends(CommonPathParams)) -> Any:
    '''
    Убирает лайк
    '''


@router.post('/comments', status_code=HTTPStatus.CREATED.value, response_model=Comment)
async def add_comment(commons: CommonPathParams = Depends(CommonPathParams)) -> Any:
    '''
    Добавляет комментарий
    '''


@router.delete('/comments/{comment_id}', status_code=HTTPStatus.NO_CONTENT.value)
async def delete_comment(commons: CommonPathParams = Depends(CommonPathParams)) -> Any:
    '''
    Удаляет комментарий
    '''


@router.post('/comments/{comment_id}/likes', status_code=HTTPStatus.CREATED.value)
async def like_comment(commons: CommonPathParams = Depends(CommonPathParams)) -> Any:
    '''
    Ставит лайк комментарию
    '''


@router.delete('/comments/{comment_id}/like', status_code=HTTPStatus.NO_CONTENT.value)
async def remove_like_comment(
    commons: CommonPathParams = Depends(CommonPathParams),
) -> Any:
    '''
    Убирает лайк с комментария
    '''
