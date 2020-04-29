import pytest
from final_project.data_access_layer.post import PostDAL
from final_project.exceptions import PostDALNotExistsError
from final_project.image_processor.worker import _add_post_to_db


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


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post')
async def test_get_post_when_post_exists():
    res = await PostDAL.get_post(1)
    assert res.user.id == 1
    assert res.comments == []
    assert res.likes == []


# @pytest.fixture()
# def _like_post():


@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post')
def test_get_post_when_post_contains_likes():
    pass
