import pytest
from final_project.data_access_layer.post import PostDAL
from final_project.database.database import create_session
from final_project.database.models import Post
from final_project.exceptions import PostDALError, PostDALNotExistsError, StorageError
from final_project.image_processor.worker import _add_post_to_db
from final_project.messages import Message
from mock import AsyncMock


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
    patched_storage_client.get_image_from_storage_async = AsyncMock(
        return_value=b'1234'
    )
    return patched_storage_client


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_post', 'mock_get_image_from_storage'
)
async def test_get_post_when_post_exists():
    res = await PostDAL.get_post(1)
    assert res.user.id == 1
    assert res.comments == []
    assert res.likes == []


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post')
async def test__get_post_when_image_does_not_exists_on_storage(patched_storage_client):
    patched_storage_client.get_image_from_storage_async = AsyncMock(
        side_effect=StorageError(Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value)
    )
    with pytest.raises(PostDALError):
        await PostDAL.get_post(1)


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_post', 'mock_get_image_from_storage', '_add_like'
)
async def test_get_post_when_post_contains_likes(out_user_first):
    post = await PostDAL.get_post(1)
    likes = post.likes
    assert len(likes) == 1
    assert likes[0] == out_user_first


@pytest.fixture(params=[1, 2])
def id_(request):
    return request.param


@pytest.fixture()
def users(out_user_first, out_user_second):
    return [out_user_first, out_user_second]


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post', '_add_second_user')
async def test_like_post_returns_expected_value(id_, users):
    res = await PostDAL.like(1, id_)
    assert len(res) == 1
    user = res[0]
    assert users[id_ - 1] == user


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post', '_add_second_user')
async def test_like_post_save_like_in_db(id_, users):
    await PostDAL.like(1, id_)
    with create_session() as session:
        post = session.query(Post).filter(Post.id == 1).one()
        likes = post.likes
        assert len(likes) == 1
        assert likes[0].id == id_


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_like_post_raises_error_if_post_does_not_exists():
    with pytest.raises(PostDALNotExistsError):
        await PostDAL.like(1, 1)


@pytest.fixture()
async def _add_like():
    await PostDAL.like(1, 1)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post', '_add_like')
async def test_like_post_raises_error_if_like_from_this_user_already_exists():
    with pytest.raises(PostDALError):
        await PostDAL.like(1, 1)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post', '_add_like')
async def test_remove_like_deletes_it_in_db():
    await PostDAL.remove_like(1, 1)
    with create_session() as session:
        post = session.query(Post).filter(Post.id == 1).one()
        assert len(post.likes) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_post', '_add_like', '_add_second_user'
)
async def test_remove_like_deletes_it_in_db_with_multiple_likes_case():
    await PostDAL.like(1, 2)
    await PostDAL.remove_like(1, 1)
    with create_session() as session:
        post = session.query(Post).filter(Post.id == 1).one()
        assert len(post.likes) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post')
async def test_remove_like_if_like_exists_will_raises_error():
    with pytest.raises(PostDALNotExistsError):
        await PostDAL.remove_like(1, 1)
