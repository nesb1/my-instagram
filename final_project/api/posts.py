from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, File, UploadFile
from final_project.models import Post

router = APIRouter()


@router.get('/', response_model=List[Post])
async def get_posts(user_id: int) -> Any:
    '''
    Возвращает список постов пользователя
    '''


# in_post: InPost
@router.post('/', status_code=HTTPStatus.CREATED.value)
async def add_post(user_id: int, file: UploadFile = File(...)) -> Any:
    return file.filename
    '''
    Возвращает запись, которая была создана
    '''
