from http import HTTPStatus

import pytest
from final_project.exceptions import StorageClientError, StorageError
from final_project.messages import Message
from final_project.models import Image
from final_project.storage_client import get_image_from_storage, save_image_to_storage, save_image_to_storage_async, \
    get_image_from_storage_async
from final_project.utils import encode_bytes_to_base64


@pytest.fixture()
def mock_add_image_to_storage_async(mocker):
    return mocker.patch('final_project.storage_client._add_image_to_storage_async')


@pytest.fixture()
def base64_2x2_image(image_2x2_in_bytes):
    return encode_bytes_to_base64(image_2x2_in_bytes)


@pytest.mark.asyncio
async def test_save_image_to_storage_when_got_unexpecting_response_status_async(mock_add_image_to_storage_async,
                                                                                base64_2x2_image):
    mock_add_image_to_storage_async.side_effect = StorageClientError(
        HTTPStatus.BAD_REQUEST.value, Message.BYTES_ARE_NOT_A_IMAGE.value
    )
    with pytest.raises(StorageError):
        await save_image_to_storage_async(base64_2x2_image, 1)


@pytest.mark.asyncio
async def test_save_image_to_storage_returns_path_when_success_async(mock_add_image_to_storage_async, base64_2x2_image):
    mock_add_image_to_storage_async.return_value = {'path': 'path'}
    res = await save_image_to_storage_async(base64_2x2_image, user_id=1)
    assert res == 'path'


@pytest.fixture()
def mock_get_image_from_storage_async(mocker):
    return mocker.patch('final_project.storage_client._get_image_from_storage_async')


@pytest.mark.asyncio
async def test_get_image_from_storage_returns_image_when_success_async(mock_get_image_from_storage_async,
                                                                       base64_2x2_image):
    mock_get_image_from_storage_async.return_value = Image(image=base64_2x2_image)
    res = await get_image_from_storage_async('path')
    assert res


@pytest.mark.asyncio
async def test_get_image_from_storage_when_got_unexpecting_response_status_async(mock_get_image_from_storage_async,
                                                                                 base64_2x2_image):
    mock_get_image_from_storage_async.side_effect = StorageClientError(HTTPStatus.NOT_FOUND.value,
                                                                       Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value)
    with pytest.raises(StorageError):
        await get_image_from_storage_async('path')


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
def mock_get_image_from_storage(mocker):
    return mocker.patch('final_project.storage_client._get_image_from_storage')


@pytest.fixture()
def mock_add_image_to_storage(mocker):
    return mocker.patch('final_project.storage_client._add_image_to_storage')


def test_get_image_from_storage_returns_image_when_success(
        mock_get_image_from_storage, base64_2x2_image
):
    mock_get_image_from_storage.return_value = Image(image=base64_2x2_image)
    res = get_image_from_storage('path')
    assert res


def test_get_image_from_storage_when_got_unexpecting_response_status(
        mock_get_image_from_storage, base64_2x2_image
):
    mock_get_image_from_storage.side_effect = StorageClientError(
        HTTPStatus.NOT_FOUND.value, Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value
    )
    with pytest.raises(StorageError):
        get_image_from_storage('path')
