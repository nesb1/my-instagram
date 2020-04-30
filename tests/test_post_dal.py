import pytest
from mock import AsyncMock

from final_project.data_access_layer.post import PostDAL
from final_project.exceptions import PostDALNotExistsError, StorageError, PostDALError
from final_project.image_processor.worker import _add_post_to_db
from final_project.messages import Message


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_post_when_post_not_exists_will_raise_error():
    with pytest.raises(PostDALNotExistsError):
        await PostDAL.get_post(1)


@pytest.fixture()
def image_path():
    return 'test_path'


@pytest.fixture()
def _add_post(in_post, image_path):
    _add_post_to_db(1, image_path, in_post.description, in_post.location)


@pytest.fixture()
def _mocked_get_image(mocker):
    mocker.patch(
        'final_project.data_access_layer.serialization.image.get_image'
    ).return_value = b'1234'


@pytest.fixture()
def patched_storage_client(mocker):
    return mocker.patch('final_project.data_access_layer.post.storage_client')


@pytest.fixture()
def mock_get_image_from_storage(patched_storage_client):
    patched_storage_client.get_image_from_storage_async = AsyncMock(return_value=b'1234')
    return patched_storage_client


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post', 'mock_get_image_from_storage')
async def test_get_post_when_post_exists():
    res = await PostDAL.get_post(1)
    assert res.user.id == 1
    assert res.comments == []
    assert res.likes == []


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post')
async def test__get_post_when_image_does_not_exists_on_storage(patched_storage_client):
    patched_storage_client.get_image_from_storage_async = AsyncMock(side_effect=StorageError(
        Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value))
    with pytest.raises(PostDALError):
        await PostDAL.get_post(1)

@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post', 'mock_get_image_from_storage')
async def test_get_post_when_post_contains_likes():
    pass
