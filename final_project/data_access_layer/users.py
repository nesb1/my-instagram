from typing import Awaitable, Union

from final_project.database.database import create_session, run_in_threadpool
from final_project.database.models import User
from final_project.exceptions import UsersDALError
from final_project.messages import Message
from final_project.models import InUser, OutUser, UserWithTokens
from final_project.password import get_password_hash


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
    @run_in_threadpool
    def get_user(
        user_id: int, without_error: bool = False, need_tokens: bool = False
    ) -> Awaitable[Union[UserWithTokens, OutUser]]:
        with create_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user and not without_error:
                raise UsersDALError(Message.USER_DOES_NOT_EXISTS.value)
            if not user:
                return None
            if need_tokens:
                return UserWithTokens.from_orm(user)
            return OutUser.from_orm(user)
