from typing import Awaitable, List

from final_project import storage_client
from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session, run_in_threadpool
from final_project.database.models import Post as DBPost
from final_project.database.models import User
from final_project.exceptions import PostDALError, PostDALNotExistsError, StorageError
from final_project.messages import Message
from final_project.models import Base64, OutUser, Post, PostWithImage
from sqlalchemy.orm import Session


class PostDAL:
    @staticmethod
    async def get_post(post_id: int) -> PostWithImage:
        with create_session() as session:
            post = await PostDAL._get_post(post_id, session)
            try:
                image: Base64 = await storage_client.get_image_from_storage_async(
                    post.image_path
                )
            except StorageError:
                raise PostDALError(Message.IMAGE_DOES_NOT_EXISTS_ON_STORAGE.value)
            serialized_post: Post = serialize(post)
        return PostWithImage(**serialized_post.dict(), image=image)

    @staticmethod
    @run_in_threadpool
    def _get_post(post_id: int, session: Session) -> Awaitable[DBPost]:
        post: DBPost = session.query(DBPost).filter(DBPost.id == post_id).first()
        if not post:
            raise PostDALNotExistsError(Message.POST_NOT_EXISTS.value)
        return post

    @staticmethod
    def _is_user_already_like(likes: List[User], user: User):
        return user in likes

    @staticmethod
    async def like(post_id: int, user_id_who_likes: int) -> List[OutUser]:
        with create_session() as session:
            post = await PostDAL._get_post(post_id, session)
            likes = post.likes
            user = session.query(User).filter(User.id == user_id_who_likes).one()
            if PostDAL._is_user_already_like(likes, user):
                raise PostDALError(Message.USER_HAS_ALREADY_LIKE_THIS_POST.value)
            likes.append(user)
            return [OutUser.from_orm(user) for user in likes]
