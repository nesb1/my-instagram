from typing import Awaitable, List, Union

from final_project.data_access_layer.serialization import serialize
from final_project.database.database import create_session, run_in_threadpool
from final_project.database.models import User
from final_project.exceptions import UsersDALDoesNotExistsError, UsersDALError
from final_project.messages import Message
from final_project.models import InUser, OutUser, UserInDetailOut, UserWithTokens
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
                raise UsersDALError(Message.USER_ALREADY_EXISTS.value)
            new_user = User(
                username=user.username, password_hash=get_password_hash(user.password)
            )
            session.add(new_user)
            session.flush()
            return OutUser.from_orm(new_user)

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
            raise UsersDALDoesNotExistsError(Message.USER_DOES_NOT_EXISTS.value)
        return user

    @staticmethod
    def _is_user_subscribed_on_another_user(user: User, subscriptions: List[User]):
        l = list(map(lambda u: u.id, subscriptions))
        return user.id in l

    @staticmethod
    async def subscribe(
        user_id: int, want_subscribe_on_user_with_id: int
    ) -> List[OutUser]:
        if user_id == want_subscribe_on_user_with_id:
            raise UsersDALError(Message.USER_CANNOT_SUBSCRIBE_ON_HIMSELF.value)
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
                raise UsersDALError(Message.USER_ALREADY_SUBSCRIBED_ON_THIS_USER.value)
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
            raise UsersDALError(Message.USER_CANNOT_UNSUBSCRIBE_FROM_HIMSELF.value)
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
                raise UsersDALError(Message.USER_NOT_SUBSCRIBED_ON_THIS_USER.value)
            subscriptions.remove(another_user)
            return UsersDataAccessLayer._serialize_to_list_out_users(subscriptions)

    @staticmethod
    @run_in_threadpool
    def get_users_by_substring_in_username(
        substring: str,
    ) -> Awaitable[List[UserInDetailOut]]:
        with create_session() as session:
            res = session.query(User).filter(User.username.contains(substring)).all()
            return [serialize(user) for user in res]

    @staticmethod
    async def get_user_by_id(user_id: int) -> UserInDetailOut:
        with create_session() as session:
            user = await UsersDataAccessLayer._get_user(user_id, session)
            return serialize(user)
