from asyncio import create_task
from http import HTTPStatus
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from final_project.config import image_storage_settings
from final_project.exceptions import StorageClientError, StorageError
from final_project.models import Base64, ImagePath, ImageWithPath

URL = f'http://{image_storage_settings.address}:{image_storage_settings.port}'
IMAGES = f'{URL}/images'
USER_IMAGES = f'{URL}/user-images'


async def _get_image_from_storage_async(
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(IMAGES, params=params) as response:
            status = response.status
            if status != HTTPStatus.OK.value:
                raise StorageClientError(await response.json())
            return await response.json()


async def get_image_from_storage_async(path: str) -> ImageWithPath:
    try:
        param = {'image_path': path}
        return ImageWithPath.parse_obj(await _get_image_from_storage_async(param))
    except StorageClientError as e:
        raise StorageError(str(e))


def _add_image_to_storage(json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    response = requests.post(IMAGES, json=json)
    status = response.status_code
    if status != HTTPStatus.CREATED.value:
        raise StorageClientError(response.json())
    return response.json()


def save_image_to_storage(img: Base64, user_id: int) -> str:
    try:
        json = {'user_id': user_id, 'image': img.decode()}
        return ImagePath.parse_obj(_add_image_to_storage(json)).path
    except StorageClientError as error:
        raise StorageError(str(error))


async def _get_all_user_images(user_id: int) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{USER_IMAGES}/{user_id}') as response:
            status = response.status
            if status != HTTPStatus.OK.value:
                raise StorageClientError(await response.json())
            return await response.json()


async def get_all_user_images(user_id: int) -> List[ImageWithPath]:
    try:
        res = await _get_all_user_images(user_id)
    except StorageClientError as e:
        raise StorageError(str(e))
    return [ImageWithPath.parse_obj(item) for item in res]


async def get_images(paths: List[ImagePath]) -> List[ImageWithPath]:
    tasks = [create_task(get_image_from_storage_async(p.path)) for p in paths]
    return [await t for t in tasks]
