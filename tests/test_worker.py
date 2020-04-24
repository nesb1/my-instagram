from datetime import datetime
from pathlib import Path

import pytest
from final_project.config import image_cutting_settings
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import create_session
from final_project.database.models import MarkedUser, Post
from final_project.image_processor.image import MyImage
from final_project.image_processor.worker import Processor, process_image
from final_project.messages import Message
from final_project.redis_keys import RedisKey
from redis import Redis


@pytest.fixture()
def mock_read_image(mocker, image_2x2):
    mock = mocker.patch('final_project.image_processor.image.open_image')
    mock.return_value = image_2x2
    return mock


@pytest.fixture()
def _mock_cut(mocker, image_2x2):
    mock = mocker.patch.object(MyImage, 'cut')
    mock.return_value = image_2x2


@pytest.fixture()
def path():
    return Path()


@pytest.fixture()
def _mock_save(mocker, path):
    mock = mocker.patch.object(MyImage, 'save')
    mock.return_value = path


@pytest.fixture()
def _mock_processor(mocker):
    mocker.patch.object(Processor, 'on_success')
    mocker.patch.object(Processor, 'on_failure')


@pytest.mark.usefixtures('_add_user', '_mock_cut', '_mock_save', '_mock_processor')
def test_process_image_will_call_read_cut_and_save(
    in_post, mock_read_image, image_2x2, uuid
):
    fake_image_bytes = b'123'
    in_post.image = fake_image_bytes
    user_id: int = 1
    process_image(user_id, in_post, uuid)
    MyImage.cut.assert_called_once_with(image_cutting_settings.aspect_resolution)
    MyImage.save.assert_called_once_with(user_id)


@pytest.fixture()
def post_id():
    return 1


@pytest.mark.usefixtures('_mock_redis')
def test_on_success_save_res_on_redis(uuid, post_id):
    Processor.on_success(uuid, post_id)
    Redis.hmset.assert_called_once_with(RedisKey.SOLVED_TASKS.value, {uuid: post_id})
    Redis.srem(RedisKey.TASKS_IN_PROGRESS.value, uuid)


@pytest.mark.usefixtures('_mock_redis')
def test_on_success_returns_expected_value(uuid, post_id):
    res = Processor.on_success(uuid, post_id)
    assert res.post_id == post_id
    assert res.error is None


@pytest.mark.usefixtures('_mock_redis')
def test_on_failure_save_data_to_redis(uuid):
    Processor.on_failure(uuid, Message.INVALID_IMAGE.value)
    Redis.hmset.assert_called_once_with(
        RedisKey.FALLEN_TASKS.value, {uuid: Message.INVALID_IMAGE.value}
    )
    Redis.srem(RedisKey.TASKS_IN_PROGRESS.value, uuid)


@pytest.mark.usefixtures('_mock_redis')
def test_on_failure_returns_expected_value(uuid):
    res = Processor.on_failure(uuid, Message.INVALID_IMAGE.value)
    assert res.post_id is None
    assert res.error == Message.INVALID_IMAGE.value


@pytest.fixture()
def _mock_add_marked_users(mocker):
    mocker.patch('final_project.image_processor.worker._add_marked_users')


@pytest.fixture()
def mocked_datetime(mocker):
    return mocker.patch('final_project.image_processor.worker.datetime')


@pytest.mark.usefixtures(
    '_add_user',
    '_mock_cut',
    '_mock_save',
    '_mock_processor',
    '_mock_add_marked_users',
    'mock_read_image',
)
def test_process_add_post_in_database(in_post, uuid, mocked_datetime):
    user_id = 1
    time = datetime.utcnow()
    mocked_datetime.utcnow.return_value = time
    process_image(user_id, in_post, uuid)
    with create_session() as session:
        post = session.query(Post).filter(Post.id == 1).first()
        assert post
        assert post.user_id == user_id
        assert post.location == in_post.location
        assert post.description == in_post.description
        assert post.created_at == time


@pytest.fixture()
async def _add_2_users(in_user):
    with create_session() as session:
        for i in range(2):
            in_user.username = str(i)
            session.add(await UsersDataAccessLayer.add_user(in_user))


@pytest.mark.usefixtures(
    '_add_user',
    '_add_2_users',
    '_mock_cut',
    '_mock_save',
    '_mock_processor',
    'mock_read_image',
)
def test_process_add_marked_users_to_database(in_post, uuid):
    in_post.marked_users_ids = [2, 3]
    process_image(1, in_post, uuid)
    with create_session() as session:
        records = session.query(MarkedUser).filter(MarkedUser.post_id == 1).all()
        assert len(records) == 2
        assert list(map(lambda record: record.user_id, records)) == [2, 3]
