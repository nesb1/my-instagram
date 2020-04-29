from http import HTTPStatus
from typing import Any, Dict, Optional
import urllib.parse
import aiohttp
import yarl

import requests
from final_project.config import image_storage_settings
from final_project.exceptions import StorageClientError, StorageError
from final_project.models import Base64, Image, ImagePath

URL = f'http://{image_storage_settings.address}:{image_storage_settings.port}'
IMAGES = f'{URL}/images'


async def save_image_to_storage_async(img: Base64, user_id: int) -> str:
    try:
        json = get_dict_for_saving_image(img, user_id)
        return ImagePath.parse_obj(await _add_image_to_storage_async(json)).path
    except StorageClientError as error:
        raise StorageError(str(error))


def get_dict_for_saving_image(img, user_id):
    json = {'user_id': user_id, 'image': img.decode()}
    return json


async def get_image_from_storage_async(path: str) -> Base64:
    try:
        param = get_param_for_getting_image_from_storage(path)
        return Image.parse_obj(await _get_image_from_storage_async(param)).image
    except StorageClientError as e:
        raise StorageError(str(e))


async def _get_image_from_storage_async(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(IMAGES, params=params) as response:
            status = response.status
            if status != HTTPStatus.OK.value:
                raise StorageClientError(
                    status_code=status, message=await response.json()
                )
            return await response.json()


async def _add_image_to_storage_async(json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.post(IMAGES, json=json) as response:
            status = response.status
            if status != HTTPStatus.CREATED.value:
                raise StorageClientError(
                    status_code=status, message=await response.json()
                )
            return await response.json()


def save_image_to_storage(img: Base64, user_id: int) -> str:
    try:
        json = get_dict_for_saving_image(img, user_id)
        return ImagePath.parse_obj(_add_image_to_storage(json)).path
    except StorageClientError as error:
        raise StorageError(str(error))


def get_image_from_storage(path: str) -> Base64:
    try:
        param = get_param_for_getting_image_from_storage(path)
        return Image.parse_obj(_get_image_from_storage(param)).image
    except StorageClientError as e:
        raise StorageError(str(e))


def get_param_for_getting_image_from_storage(path):
    param = {'image_path': path}
    return param


def _get_image_from_storage(
        params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    response = requests.get(IMAGES, data=params)
    status = response.status_code
    if status != HTTPStatus.OK.value:
        raise StorageClientError(
            status_code=status, message=response.json()
        )
    return response.json()


def _add_image_to_storage(
        json: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    response = requests.post(IMAGES, json=json)
    status = response.status_code
    if status != HTTPStatus.CREATED.value:
        raise StorageClientError(
            status_code=status, message=response.json()
        )
    return response.json()


