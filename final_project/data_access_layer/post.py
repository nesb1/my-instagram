from http import HTTPStatus
from typing import Awaitable, List

from final_project import storage_client
from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session, run_in_threadpool
from final_project.database.models import Post as DBPost
from final_project.database.models import User
from final_project.exceptions import DALError, StorageError
from final_project.messages import Message
from final_project.models import Base64, OutUser, Post, PostWithImage
from sqlalchemy.orm import Session


class PostDAL:
    @staticmethod
    async def get_post(post_id: int) -> PostWithImage:
        with create_session() as session:
            post = await PostDAL._get_post(post_id, session)
            try:
                image: Base64 = (
                    await storage_client.get_image_from_storage_async(post.image_path)
                ).image
            except StorageError:
                raise DALError(
                    HTTPStatus.NOT_FOUND.value,
                    Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value,
                )
            serialized_post: Post = serialize(post)  # type: ignore
        return PostWithImage(**serialized_post.dict(), image=image)

    @staticmethod
    @run_in_threadpool
    def _get_post(post_id: int, session: Session) -> Awaitable[DBPost]:
        post: DBPost = session.query(DBPost).filter(DBPost.id == post_id).first()
        if not post:
            raise DALError(HTTPStatus.NOT_FOUND.value, Message.POST_NOT_EXISTS.value)
        return post  # type: ignore

    @staticmethod
    def _is_user_has_like(likes: List[User], user: User) -> bool:
        return user in likes

    @staticmethod
    async def like(post_id: int, user_id_who_likes: int) -> List[OutUser]:
        with create_session() as session:
            post = await PostDAL._get_post(post_id, session)
            likes = post.likes
            user = await PostDAL._get_user(user_id_who_likes, session)
            if PostDAL._is_user_has_like(likes, user):
                raise DALError(
                    HTTPStatus.BAD_REQUEST.value,
                    Message.USER_HAS_ALREADY_LIKE_THIS_POST.value,
                )
            likes.append(user)
            return [OutUser.from_orm(user) for user in likes]

    @staticmethod
    @run_in_threadpool
    def _get_user(user_id: int, session: Session) -> Awaitable[User]:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return user
        raise DALError(HTTPStatus.NOT_FOUND.value, Message.USER_DOES_NOT_EXISTS.value)

    @staticmethod
    async def remove_like(post_id: int, user_id_who_wants_delete_like: int) -> None:
        with create_session() as session:
            post = await PostDAL._get_post(post_id, session)
            user = await PostDAL._get_user(user_id_who_wants_delete_like, session)
            likes = post.likes
            if not PostDAL._is_user_has_like(likes, user):
                raise DALError(
                    HTTPStatus.NOT_FOUND.value,
                    Message.USER_DID_NOT_LIKE_THIS_POST.value,
                )
            likes.remove(user)
