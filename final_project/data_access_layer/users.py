from http import HTTPStatus
from typing import Awaitable, List, Union

from final_project import storage_client, utils
from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session, run_in_threadpool
from final_project.database.models import Post as DB_Post
from final_project.database.models import User
from final_project.exceptions import DALError, PaginationError
from final_project.messages import Message
from final_project.models import (
    ImagePath,
    InUser,
    OutUser,
    PostWithImage,
    PostWithImagePath,
    UserInDetailOut,
    UserWithTokens,
)
from final_project.password import get_password_hash
from sqlalchemy.orm import Session


class UsersDataAccessLayer:
    @staticmethod
    @run_in_threadpool
    def add_user(user: InUser) -> Awaitable[OutUser]:
        """
        Добавляет пользователя в БД
        """
        with create_session() as session:
            existing_user = (
                session.query(User).filter(User.username == user.username).first()
            )
            if existing_user:
                raise DALError(
                    HTTPStatus.BAD_REQUEST.value, Message.USER_ALREADY_EXISTS.value
                )
            new_user = User(
                username=user.username, password_hash=get_password_hash(user.password)
            )
            session.add(new_user)
            session.flush()
            return OutUser.from_orm(new_user)  # type: ignore

    @staticmethod
    async def get_user(
        user_id: int, without_error: bool = False, need_tokens: bool = False
    ) -> Union[None, UserWithTokens, OutUser]:
        with create_session() as session:
            user = await UsersDataAccessLayer._get_user(user_id, session, without_error)
            if not user:
                return None
            if need_tokens:
                return UserWithTokens.from_orm(user)
            return OutUser.from_orm(user)

    @staticmethod
    @run_in_threadpool
    def _get_user(
        user_id: int, session: Session, without_error: bool = False
    ) -> Awaitable[User]:
        user = session.query(User).filter(User.id == user_id).first()
        if not user and not without_error:
            raise DALError(
                HTTPStatus.NOT_FOUND.value, Message.USER_DOES_NOT_EXISTS.value
            )
        return user

    @staticmethod
    def _is_user_subscribed_on_another_user(
        user: User, subscriptions: List[User]
    ) -> bool:
        return user.id in list(map(lambda u: u.id, subscriptions))

    @staticmethod
    async def subscribe(
        user_id: int, want_subscribe_on_user_with_id: int
    ) -> List[OutUser]:
        if user_id == want_subscribe_on_user_with_id:
            raise DALError(
                HTTPStatus.BAD_REQUEST.value,
                Message.USER_CANNOT_SUBSCRIBE_ON_HIMSELF.value,
            )
        with create_session() as session:
            user_who_wants_subscribe = await UsersDataAccessLayer._get_user(
                user_id, session
            )
            another_user = await UsersDataAccessLayer._get_user(
                want_subscribe_on_user_with_id, session
            )
            if UsersDataAccessLayer._is_user_subscribed_on_another_user(
                another_user, user_who_wants_subscribe.subscriptions
            ):
                raise DALError(
                    HTTPStatus.BAD_REQUEST.value,
                    Message.USER_ALREADY_SUBSCRIBED_ON_THIS_USER.value,
                )
            user_who_wants_subscribe.subscriptions.append(another_user)
            return UsersDataAccessLayer._serialize_to_list_out_users(
                user_who_wants_subscribe.subscriptions
            )

    @staticmethod
    def _serialize_to_list_out_users(db_objs: List[User]) -> List[OutUser]:
        return [OutUser.from_orm(user) for user in db_objs]

    @staticmethod
    async def unsubscribe(
        user_id: int, want_unsubscribe_on_user_with_id: int
    ) -> List[OutUser]:
        if user_id == want_unsubscribe_on_user_with_id:
            raise DALError(
                HTTPStatus.BAD_REQUEST.value,
                Message.USER_CANNOT_UNSUBSCRIBE_FROM_HIMSELF.value,
            )
        with create_session() as session:
            user_who_wants_unsubscribe = await UsersDataAccessLayer._get_user(
                user_id, session
            )
            another_user = await UsersDataAccessLayer._get_user(
                want_unsubscribe_on_user_with_id, session
            )
            subscriptions = user_who_wants_unsubscribe.subscriptions
            if not UsersDataAccessLayer._is_user_subscribed_on_another_user(
                another_user, subscriptions
            ):
                raise DALError(
                    HTTPStatus.BAD_REQUEST.value,
                    Message.USER_NOT_SUBSCRIBED_ON_THIS_USER.value,
                )
            subscriptions.remove(another_user)
            return UsersDataAccessLayer._serialize_to_list_out_users(subscriptions)

    @staticmethod
    @run_in_threadpool
    def get_users_by_substring_in_username(
        substring: str,
    ) -> Awaitable[List[UserInDetailOut]]:
        with create_session() as session:
            res = session.query(User).filter(User.username.contains(substring)).all()
            return [serialize(user) for user in res]  # type: ignore

    @staticmethod
    async def get_user_by_id(user_id: int) -> UserInDetailOut:
        with create_session() as session:
            user = await UsersDataAccessLayer._get_user(user_id, session)
            return serialize(user)  # type: ignore

    @staticmethod
    def _get_sorted_posts_of_all_subscriptions(user: User) -> List[DB_Post]:
        res = list(user.posts)
        for subscription in user.subscriptions:
            res.extend(subscription.posts)
        res.sort(key=lambda post: post.created_at)
        return res

    @staticmethod
    async def get_feed(user_id: int, page: int, size: int) -> List[PostWithImage]:
        posts = await UsersDataAccessLayer.get_feed_posts_with_paths(
            user_id, page, size
        )
        images = await storage_client.get_images(
            list(map(lambda p: ImagePath(path=p.image_path), posts))
        )
        return utils.join_posts_with_images(posts, images)

    @staticmethod
    async def get_feed_posts_with_paths(
        user_id: int, page: int, size: int
    ) -> List[PostWithImagePath]:
        with create_session() as session:
            user = await UsersDataAccessLayer._get_user(user_id, session)
            posts = UsersDataAccessLayer._get_sorted_posts_of_all_subscriptions(user)
            if posts:
                try:
                    return [
                        PostWithImagePath.from_orm(p)
                        for p in utils.get_pagination(posts, page, size)
                    ]
                except PaginationError as e:
                    raise DALError(HTTPStatus.BAD_REQUEST.value, str(e))
            return []
