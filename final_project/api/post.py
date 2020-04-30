from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends
from final_project.data_access_layer.auth import check_authorization
from final_project.data_access_layer.post import PostDAL
from final_project.exceptions import PostDALError, PostDALNotExistsError
from final_project.models import Comment, OutUser, PostWithImage
from starlette.responses import JSONResponse

router = APIRouter()


class CommonPathParams:
    def __init__(self, user_id: int, post_id: int) -> None:
        self.user_id = user_id
        self.post_id = post_id


@router.get('/', response_model=PostWithImage)
async def get_post(
    commons: CommonPathParams = Depends(CommonPathParams),
    user=Depends(check_authorization),
) -> Any:
    '''
    Возвращает запись
    '''
    try:
        return await PostDAL.get_post(post_id=commons.post_id)
    except PostDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


@router.post(
    '/likes', response_model=List[OutUser], status_code=HTTPStatus.CREATED.value
)
async def like(
    commons: CommonPathParams = Depends(CommonPathParams),
    user: OutUser = Depends(check_authorization),
) -> Any:
    '''
    Ставит лайк, возвращает список лайков
    '''
    try:
        return await PostDAL.like(post_id=commons.post_id, user_id_who_likes=user.id)
    except PostDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)
    except PostDALError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.BAD_REQUEST.value)


@router.delete('/like', status_code=HTTPStatus.NO_CONTENT.value)
async def remove_like(
    commons: CommonPathParams = Depends(CommonPathParams),
    user: OutUser = Depends(check_authorization),
) -> Any:
    '''
    Убирает лайк
    '''
    try:
        await PostDAL.remove_like(
            post_id=commons.post_id, user_id_who_wants_delete_like=user.id
        )
    except PostDALNotExistsError as e:
        return JSONResponse({'message': str(e)}, HTTPStatus.NOT_FOUND.value)


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
