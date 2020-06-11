from http import HTTPStatus

import pytest
from final_project.exceptions import StorageClientError, StorageError
from final_project.messages import Message
from final_project.models import ImageWithPath
from final_project.storage_client import (
    get_all_user_images,
    get_image_from_storage_async,
    save_image_to_storage,
)


@pytest.fixture()
def mock_get_image_from_storage_async(mocker):
    return mocker.patch('final_project.storage_client._get_image_from_storage_async')


@pytest.mark.asyncio
async def test_get_image_from_storage_returns_image_when_success_async(
    mock_get_image_from_storage_async, base64_2x2_image
):
    mock_get_image_from_storage_async.return_value = ImageWithPath(
        image=base64_2x2_image, path='path'
    )
    res = await get_image_from_storage_async('path')
    assert res


@pytest.mark.asyncio
async def test_get_image_from_storage_when_got_unexpecting_response_status_async(
    mock_get_image_from_storage_async, base64_2x2_image
):
    mock_get_image_from_storage_async.side_effect = StorageClientError(
        HTTPStatus.NOT_FOUND.value, Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value
    )
    with pytest.raises(StorageError):
        await get_image_from_storage_async('path')


@pytest.fixture()
def mock__get_all_user_images(mocker):
    return mocker.patch('final_project.storage_client._get_all_user_images')


@pytest.mark.asyncio
async def test_get_all_user_(mock__get_all_user_images, base64_2x2_image):
    mock__get_all_user_images.return_value = [
        {'image': base64_2x2_image, 'path': 'path'}
    ]
    res = await get_all_user_images(1)
    assert len(res) == 1
    assert res[0] == ImageWithPath(image=base64_2x2_image, path='path')


@pytest.mark.asyncio
async def test_get_all_user_posts_when_user_does_not_have_images(
    mock__get_all_user_images, base64_2x2_image
):
    mock__get_all_user_images.side_effect = StorageClientError(
        HTTPStatus.NOT_FOUND.value, Message.USER_DOES_NOT_HAVE_IMAGES.value
    )
    with pytest.raises(StorageError):
        await get_all_user_images(1)


def test_save_image_to_storage_when_got_unexpecting_response_status(
    mock_add_image_to_storage, base64_2x2_image
):
    mock_add_image_to_storage.side_effect = StorageClientError(
        HTTPStatus.BAD_REQUEST.value, Message.BYTES_ARE_NOT_A_IMAGE.value
    )
    with pytest.raises(StorageError):
        save_image_to_storage(base64_2x2_image, 1)


def test_save_image_to_storage_returns_path_when_success(
    mock_add_image_to_storage, base64_2x2_image
):
    mock_add_image_to_storage.return_value = {'path': 'path'}
    res = save_image_to_storage(base64_2x2_image, user_id=1)
    assert res == 'path'


@pytest.fixture()
def mock_add_image_to_storage(mocker):
    return mocker.patch('final_project.storage_client._add_image_to_storage')
