import asyncio
from http import HTTPStatus
from typing import Any, Dict, Optional
import urllib.parse
import aiohttp
import yarl

from final_project.config import image_storage_settings
from final_project.exceptions import StorageClientError, StorageError
from final_project.models import Base64, ImagePath, Image, ImageWithPath

URL = f'http://{image_storage_settings.address}:{image_storage_settings.port}'
IMAGES = f'{URL}/images'


async def save_image_to_storage(img: Base64, user_id: int) -> str:
    try:
        json = {'user_id': user_id, 'image': img.decode()}
        return ImagePath.parse_obj(await _add_image_to_storage(json)).path
    except StorageClientError as error:
        raise StorageError(str(error))


async def get_image_from_storage(path: str) -> Base64:
    try:
        param = {'image_path': path}
        return Image.parse_obj(await _get_image_from_storage(param)).image
    except StorageClientError as e:
        raise StorageError(str(e))


async def _get_image_from_storage(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(IMAGES, params=params) as response:
            status = response.status
            if status != HTTPStatus.OK.value:
                raise StorageClientError(
                    status_code=status, message=await response.json()
                )
            return await response.json()


async def _add_image_to_storage(json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.post(IMAGES, json=json) as response:
            status = response.status
            if status != HTTPStatus.CREATED.value:
                raise StorageClientError(
                    status_code=status, message=await response.json()
                )
            return await response.json()
