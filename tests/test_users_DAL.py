import pytest
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import create_session
from final_project.database.models import User
from final_project.exceptions import UsersDALDoesNotExistsError, UsersDALError
from final_project.image_processor.worker import _add_post_to_db
from final_project.models import ImageWithPath
from final_project.password import get_password_hash
from mock import AsyncMock


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_add_new_user_returns_expected_value(in_user):
    actual = await UsersDataAccessLayer.add_user(in_user)
    assert actual.username == in_user.username
    assert actual.id == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_add_new_user_adds_data_to_database(in_user):
    with create_session() as s:
        user = s.query(User).filter(User.id == 1).first()
        assert user
        assert user.username == in_user.username


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_add_user_that_already_exists_will_raise_error(in_user):
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.add_user(in_user)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_add_user_function_encrypts_password(in_user):
    with create_session() as s:
        user = s.query(User).filter(User.id == 1).first()
        assert user.password_hash == get_password_hash(in_user.password)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_get_existing_user_returns_expected_value(username):
    user = await UsersDataAccessLayer.get_user(1)
    assert user
    assert user.username == username


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_not_existing_user_raises_error():
    with pytest.raises(UsersDALDoesNotExistsError):
        await UsersDataAccessLayer.get_user(1)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_not_existing_user_with_show_error_true_returns_none():
    assert await UsersDataAccessLayer.get_user(1, without_error=True) is None


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_subscribe_on_user_that_does_not_exists_raises_error():
    with pytest.raises(UsersDALDoesNotExistsError):
        await UsersDataAccessLayer.subscribe(1, 2)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_subscribe_on_myself_will_raise_error():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.subscribe(1, 1)


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_second_user', '_subscribe_on_user'
)
async def test_subscribe_two_times_will_raises_error():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.subscribe(1, 2)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_second_user')
async def test_subscribe_on_user_returns_expected_value(out_user_second):
    res = await UsersDataAccessLayer.subscribe(1, 2)
    assert len(res) == 1
    assert res[0] == out_user_second


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_second_user')
async def test_subscribe_on_user_change_data_on_db(out_user_first):
    await UsersDataAccessLayer.subscribe(1, 2)
    with create_session() as session:
        user = session.query(User).filter(User.id == 1).one()
        subscriptions = user.subscriptions
        assert len(subscriptions) == 1
        user2: User = session.query(User).filter(User.id == 2).one()
        assert user2 in subscriptions
        subscribers = user2.subscribers
        assert len(subscribers) == 1
        assert user in subscribers


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_second_user', '_subscribe_on_user'
)
async def test_unsubscribe_from_user_returns_expected_value(out_user_second):
    res = await UsersDataAccessLayer.unsubscribe(1, 2)
    assert len(res) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_second_user')
async def test_unsubscribe_from_user_that_not_in_subscriptions():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.unsubscribe(1, 2)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_unsubscribe_from_myself():
    with pytest.raises(UsersDALError):
        await UsersDataAccessLayer.unsubscribe(1, 1)


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_find_user_by_substring_with_similar_names(in_user, second_in_user):
    in_user.username = '123'
    second_in_user.username = '12'
    await UsersDataAccessLayer.add_user(in_user)
    await UsersDataAccessLayer.add_user(second_in_user)
    res = await UsersDataAccessLayer.get_users_by_substring_in_username('1')
    assert len(res) == 2


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_find_user_by_substring_when_substrings_are_difference(
    in_user, second_in_user
):
    in_user.username = '1'
    second_in_user.username = '2'
    await UsersDataAccessLayer.add_user(in_user)
    await UsersDataAccessLayer.add_user(second_in_user)
    res = await UsersDataAccessLayer.get_users_by_substring_in_username('1')
    assert len(res) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_find_user_by_substring_with_not_exists_name(in_user):
    in_user.username = '1'
    await UsersDataAccessLayer.add_user(in_user)
    res = await UsersDataAccessLayer.get_users_by_substring_in_username('2')
    assert len(res) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user')
async def test_get_user_by_id():
    res = await UsersDataAccessLayer.get_user_by_id(1)
    assert res


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db')
async def test_get_user_by_id_if_user_does_not_exists():
    with pytest.raises(UsersDALDoesNotExistsError):
        await UsersDataAccessLayer.get_user_by_id(1)


@pytest.fixture()
def post_adding_commons():
    return '1', '1', '1'


@pytest.fixture()
def _add_post_from_second_user(post_adding_commons):
    _add_post_to_db(2, *post_adding_commons)


@pytest.fixture()
def _add_post_from_third_user(post_adding_commons):
    _add_post_to_db(3, *post_adding_commons)


@pytest.fixture()
def _mock_storage_client(mocker):
    mocker.patch(
        'final_project.data_access_layer.users.storage_client'
    ).get_images = AsyncMock()


@pytest.fixture()
def mock_join_posts_with_image(mocker):
    return mocker.patch(
        'final_project.data_access_layer.users.utils.join_posts_with_images'
    )


@pytest.fixture()
def image_with_path(base64_2x2_image):
    return ImageWithPath(image=base64_2x2_image, path='1')


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_mock_storage_client')
async def test_get_feed_when_feed_clear():
    res = await UsersDataAccessLayer.get_feed(1, 1, 10)
    assert len(res) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures('_init_db', '_add_user', '_add_post')
async def test_get_feed_when_user_add_post():
    res = await UsersDataAccessLayer.get_feed_posts_with_paths(1, 1, 10)
    assert len(res) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db', '_add_user', '_add_second_user', '_add_post_from_second_user'
)
async def test_get_feed_when_subscription_add_post(image_with_path):
    await UsersDataAccessLayer.subscribe(1, 2)
    res = await UsersDataAccessLayer.get_feed_posts_with_paths(1, 1, 10)
    assert len(res) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db',
    '_add_user',
    '_add_second_user',
    '_add_third_user',
    '_add_post_from_second_user',
    '_add_post_from_third_user',
)
async def test_get_feed_when_two_subscriptions_add_post(image_with_path):
    await UsersDataAccessLayer.subscribe(1, 2)
    await UsersDataAccessLayer.subscribe(1, 3)
    res = await UsersDataAccessLayer.get_feed_posts_with_paths(1, 1, 10)
    assert len(res) == 2
    res_copy = res.copy()
    res_copy.sort(key=lambda post: post.created_at)
    assert res_copy == res


@pytest.mark.asyncio
@pytest.mark.usefixtures(
    '_init_db',
    '_add_user',
    '_add_post',
    '_add_second_user',
    '_add_third_user',
    '_add_post_from_second_user',
    '_add_post_from_third_user',
)
async def test_get_feed_when_two_subscriptions_add_post_and_user_add_post_too(
    image_with_path,
):
    await UsersDataAccessLayer.subscribe(1, 2)
    await UsersDataAccessLayer.subscribe(1, 3)
    res = await UsersDataAccessLayer.get_feed_posts_with_paths(1, 1, 10)
    assert len(res) == 3
    res_copy = res.copy()
    res_copy.sort(key=lambda post: post.created_at)
    assert res_copy == res
