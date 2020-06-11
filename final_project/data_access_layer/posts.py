from http import HTTPStatus
from typing import List, Optional
from uuid import uuid4

from final_project import storage_client
from final_project.data_access_layer.users import UsersDataAccessLayer
from final_project.database.database import create_session
from final_project.database.models import User
from final_project.exceptions import DALError, StorageError
from final_project.image_processor.worker import process_image
from final_project.messages import Message
from final_project.models import (
    ImageWithPath,
    InPost,
    PostWithImage,
    TaskResponse,
    WorkerResult,
)
from final_project.redis import RedisInstances
from final_project.redis_keys import RedisKey
from final_project.utils import join_posts_with_images


class PostsDAL:
    @staticmethod
    async def add_post(user_id: int, post: InPost) -> TaskResponse:
        user = await UsersDataAccessLayer.get_user(user_id, without_error=True)
        if not user:
            raise DALError(
                HTTPStatus.NOT_FOUND.value, Message.USER_DOES_NOT_EXISTS.value
            )
        ids = post.marked_users_ids
        if ids is not None and (
            not await PostsDAL._are_marked_users_correct(ids) or user_id in ids
        ):
            raise DALError(
                HTTPStatus.BAD_REQUEST.value, Message.INCORRECTLY_MARKED_USERS.value
            )
        task_id = str(uuid4())
        job = RedisInstances.redis_queue().enqueue(
            process_image, user_id, post, task_id
        )
        async_redis = await RedisInstances.async_redis()
        async_redis.sadd(RedisKey.TASKS_IN_PROGRESS.value, task_id)
        job_result: Optional[WorkerResult] = job.result
        if job_result:
            if job_result.post_id:
                return TaskResponse(
                    task_id=task_id,
                    status=Message.POST_READY.value,
                    post_id=job_result.post_id,
                )
            return TaskResponse(
                task_id=task_id,
                status=Message.POST_TASK_FALLEN.value,
                error_text=job_result.error,
            )
        return TaskResponse(
            task_id=task_id, status=Message.POST_ACCEPTED_FOR_PROCESSING.value
        )

    @staticmethod
    async def _are_marked_users_correct(marked_users_ids: List[int]) -> bool:
        s = set(marked_users_ids)
        if len(s) != len(marked_users_ids):
            return False
        return all(
            [
                await UsersDataAccessLayer.get_user(u_id, without_error=True)
                for u_id in marked_users_ids
            ]
        )

    @staticmethod
    async def get_task_status(task_id: str) -> TaskResponse:
        redis = await RedisInstances.async_redis()
        solved_task: Optional[bytes] = (
            await redis.hmget(RedisKey.SOLVED_TASKS.value, task_id)
        )[0]
        if solved_task:
            return TaskResponse(
                task_id=task_id,
                status=Message.POST_READY.value,
                post_id=solved_task.decode(),
            )
        fallen_task: Optional[bytes] = (
            await redis.hmget(RedisKey.FALLEN_TASKS.value, task_id)
        )[0]
        if fallen_task:
            return TaskResponse(
                task_id=task_id,
                status=Message.POST_TASK_FALLEN.value,
                error_text=fallen_task.decode(),
            )
        if await redis.sismember(RedisKey.TASKS_IN_PROGRESS.value, task_id):
            return TaskResponse(
                task_id=task_id, status=Message.POST_ACCEPTED_FOR_PROCESSING.value
            )
        raise DALError(HTTPStatus.NOT_FOUND.value, Message.TASK_NOT_EXISTS.value)

    @staticmethod
    async def get_posts(user_id: int) -> List[PostWithImage]:
        with create_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise DALError(
                    HTTPStatus.NOT_FOUND.value, Message.USER_DOES_NOT_EXISTS.value
                )
            posts = user.posts
            if not posts:
                raise DALError(
                    HTTPStatus.NOT_FOUND.value, Message.POSTS_DO_NOT_EXIST.value
                )
            try:
                images: List[ImageWithPath] = await storage_client.get_all_user_images(
                    user_id
                )
            except StorageError as e:
                raise DALError(HTTPStatus.BAD_REQUEST.value, e)
            return join_posts_with_images(posts, images)
