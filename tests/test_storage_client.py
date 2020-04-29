from http import HTTPStatus

import pytest
from final_project.exceptions import StorageClientError, StorageError
from final_project.image_processor.storage_client import save_image_to_storage, get_image_from_storage
from final_project.messages import Message
from final_project.models import ImageWithPath, ImagePath, Image
from final_project.utils import encode_bytes_to_base64


@pytest.fixture()
def mock_add_image_to_storage(mocker):
    return mocker.patch(
        'final_project.image_processor.storage_client._add_image_to_storage'
    )


@pytest.fixture()
def base64_2x2_image(image_2x2_in_bytes):
    return encode_bytes_to_base64(image_2x2_in_bytes)


@pytest.mark.asyncio
async def test_save_image_to_storage_when_got_unexpecting_response_status(mock_add_image_to_storage, base64_2x2_image):
    mock_add_image_to_storage.side_effect = StorageClientError(
        HTTPStatus.BAD_REQUEST.value, Message.BYTES_ARE_NOT_A_IMAGE.value
    )
    with pytest.raises(StorageError):
        await save_image_to_storage(base64_2x2_image, 1)


@pytest.mark.asyncio
async def test_save_image_to_storage_returns_path_when_success(mock_add_image_to_storage, base64_2x2_image):
    mock_add_image_to_storage.return_value = {'path': 'path'}
    res = await save_image_to_storage(base64_2x2_image, user_id=1)
    assert res == 'path'


@pytest.fixture()
def mock_get_image_from_storage(mocker):
    return mocker.patch('final_project.image_processor.storage_client._get_image_from_storage')


@pytest.mark.asyncio
async def test_get_image_from_storage_returns_image_when_success(mock_get_image_from_storage, base64_2x2_image):
    mock_get_image_from_storage.return_value = Image(image=base64_2x2_image)
    res = await get_image_from_storage('path')
    assert res


@pytest.mark.asyncio
async def test_get_image_from_storage_when_got_unexpecting_response_status(mock_get_image_from_storage,
                                                                           base64_2x2_image):
    mock_get_image_from_storage.side_effect = StorageClientError(HTTPStatus.NOT_FOUND.value,
                                                                 Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value)
    with pytest.raises(StorageError):
        await get_image_from_storage('path')
