import pytest
from final_project.data_access_layer.posts import PostsDAL
from final_project.exceptions import PostsDALError
from final_project.image_processor.worker import process_image
from final_project.messages import Message
from final_project.redis_keys import RedisKey
from redis import Redis
from rq import Queue


@pytest.fixture()
def _mock_redis_queue(mocker):
    mocker.patch.object(Queue, 'enqueue')
    Queue.enqueue.return_value.result = None


@pytest.fixture()
def _mock_uuid4(mocker, uuid):
    mock = mocker.patch('final_project.data_access_layer.posts.uuid4')
    mock.return_value = uuid


@pytest.mark.asyncio
async def test_add_post_raises_error_if_user_does_not_exists(in_post):
    with pytest.raises(PostsDALError):
        await PostsDAL.add_post(1, in_post)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user')
async def test_add_post_raises_error_if_marked_users_are_not_correct(in_post):
    in_post.marked_users_ids = [2, 3]
    with pytest.raises(PostsDALError):
        await PostsDAL.add_post(1, in_post)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_redis_queue')
async def test_add_post_raises_error_if_marked_himself(in_post):
    in_post.marked_users_ids = [1]
    with pytest.raises(PostsDALError):
        await PostsDAL.add_post(1, in_post)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_redis_queue', '_mock_redis', '_mock_uuid4')
async def test_add_post_add_task_to_redis_queue(in_post, uuid):
    await PostsDAL.add_post(1, in_post)
    Queue.enqueue.assert_called_once_with(process_image, 1, in_post, uuid)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_redis_queue', '_mock_redis', '_mock_uuid4')
async def test_add_post_add_task_to_redis_as_processing(in_post, uuid):
    await PostsDAL.add_post(1, in_post)
    Redis.sadd.assert_called_once_with(RedisKey.TASKS_IN_PROGRESS.value, uuid)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_add_user', '_mock_redis_queue', '_mock_redis', '_mock_uuid4')
async def test_add_post_add_task_return_expected_value(in_post, uuid):
    res = await PostsDAL.add_post(1, in_post)
    assert res.status == Message.POST_ACCEPTED_FOR_PROCESSING.value
    assert res.task_id == uuid
