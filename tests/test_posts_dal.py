import pytest
from aioredis import Redis
from final_project.data_access_layer.posts import PostsDAL
from final_project.exceptions import PostsDALError, PostsDALNotExistsError
from final_project.image_processor.worker import process_image
from final_project.messages import Message
from final_project.redis import RedisInstances
from final_project.redis_keys import RedisKey
from rq import Queue


@pytest.fixture()
async def async_redis(_mock_async_redis):
    return await RedisInstances.async_redis()


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
@pytest.mark.usefixtures(
    '_add_user', '_mock_redis_queue', '_mock_uuid4', '_mock_async_redis'
)
async def test_add_post_add_task_to_redis_queue(in_post, uuid):
    await PostsDAL.add_post(1, in_post)
    Queue.enqueue.assert_called_once_with(process_image, 1, in_post, uuid)


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_add_user', '_mock_redis_queue', '_mock_uuid4', '_mock_async_redis'
)
async def test_add_post_add_task_to_redis_as_processing(in_post, uuid):
    await PostsDAL.add_post(1, in_post)
    (await RedisInstances.async_redis()).sadd.assert_called_once_with(
        RedisKey.TASKS_IN_PROGRESS.value, uuid
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_add_user', '_mock_redis_queue', '_mock_async_redis', '_mock_uuid4'
)
async def test_add_post_add_task_return_expected_value(in_post, uuid):
    res = await PostsDAL.add_post(1, in_post)
    assert res.status == Message.POST_ACCEPTED_FOR_PROCESSING.value
    assert res.task_id == uuid


@pytest.mark.asyncio
@pytest.mark.usefixtures('_mock_async_redis')
async def test_get_task_status_when_task_solved(async_redis):
    task_id = '123'
    async_redis.hmget.return_value = [b'1']
    res = await PostsDAL.get_task_status(task_id)
    assert res.post_id == 1
    assert res.status == Message.POST_READY.value
    async_redis.hmget.assert_called_once_with(RedisKey.SOLVED_TASKS.value, task_id)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_mock_async_redis')
async def test_get_task_status_when_task_fallen(async_redis):
    task_id = '123'
    async_redis.hmget.side_effect = [[None], [Message.INVALID_IMAGE.value.encode()]]
    res = await PostsDAL.get_task_status(task_id)
    assert res.status == Message.POST_TASK_FALLEN.value
    assert res.error_text == Message.INVALID_IMAGE.value


@pytest.mark.asyncio
@pytest.mark.usefixtures('_mock_async_redis')
async def test_get_task_status_when_task_not_processed_yet(async_redis):
    task_id = '123'
    async_redis.hmget.side_effect = [[None], [None]]
    Redis.sismember.return_value = 1
    res = await PostsDAL.get_task_status(task_id)
    assert res.status == Message.POST_ACCEPTED_FOR_PROCESSING.value


@pytest.mark.asyncio
@pytest.mark.usefixtures('_mock_async_redis')
async def test_get_task_status_when_task_not_exists(async_redis):
    task_id = '123'
    async_redis.hmget.side_effect = [[None], [None]]
    async_redis.sismember.return_value = 0
    with pytest.raises(PostsDALNotExistsError):
        await PostsDAL.get_task_status(task_id)
