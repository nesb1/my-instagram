from binascii import Error
from datetime import datetime
from time import sleep
from typing import List, Optional

from final_project.config import image_cutting_settings, redis_settings
from final_project.database.database import create_session
from final_project.database.models import Post, User
from final_project.exceptions import MyImageError, StorageError
from final_project.image_processor.image import MyImage
from final_project.messages import Message
from final_project.models import InPost, WorkerResult
from final_project.redis_keys import RedisKey
from final_project.utils import decode_base64_to_bytes
from redis import Redis

redis = Redis(redis_settings.redis_address)


class Processor:
    @staticmethod
    def on_success(task_id: str, post_id: int) -> WorkerResult:
        redis.hmset(RedisKey.SOLVED_TASKS.value, {task_id: post_id})
        redis.srem(RedisKey.TASKS_IN_PROGRESS.value, task_id)
        return WorkerResult(post_id=post_id)

    @staticmethod
    def on_failure(task_id: str, error: str) -> WorkerResult:
        redis.hmset(RedisKey.FALLEN_TASKS.value, {task_id: error})
        redis.srem(RedisKey.TASKS_IN_PROGRESS.value, task_id)
        return WorkerResult(error=error)


def _add_post_to_db(
        user_id: int, image_path: str, description: str, location: Optional[str]
) -> int:
    with create_session() as session:
        post = Post(
            user_id=user_id,
            image_path=image_path,
            description=description,
            location=location,
            created_at=datetime.utcnow(),
        )
        session.add(post)
        session.flush()
        return post.id


def _add_marked_users(ids: List[int], post_id: int) -> None:
    with create_session() as session:
        post = session.query(Post).filter(Post.id == post_id).first()
        for id_ in ids:
            user = session.query(User).filter(User.id == id_).first()
            post.marked_users.append(user)
        session.add(post)


def process_image(user_id: int, post: InPost, task_id: str) -> WorkerResult:
    '''
    Обрезает изображение до квадратного, сохраняет в файловое хранилище
    и фиксирует путь к изображению в бд
    '''
    try:
        bytes_ = decode_base64_to_bytes(post.image)
    except Error:
        return Processor.on_failure(task_id, Message.INVALID_BASE64_PADDING.value)
    try:
        image = MyImage(bytes_)
        image.cut(image_cutting_settings.aspect_resolution)
        image_path = image.save(user_id)
    except (MyImageError, StorageError) as e:
        return Processor.on_failure(task_id, str(e))
    post_id = _add_post_to_db(
        user_id=user_id,
        image_path=image_path,
        description=post.description,
        location=post.location,
    )
    ids = post.marked_users_ids
    if ids:
        _add_marked_users(ids, post_id)
    Processor.on_success(task_id, post_id)
