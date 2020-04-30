from functools import singledispatch
from typing import List

from final_project.database.database import Base
from final_project.database.models import Comment as DB_Comment
from final_project.database.models import Post as DB_Post
from final_project.database.models import User as DB_User
from final_project.models import Comment, OutUser, Post, UserInDetailOut
from pydantic import BaseModel


@singledispatch
def serialize(orm_obj: Base) -> BaseModel:
    raise ValueError()


@serialize.register
def _(orm_obj: DB_Comment) -> BaseModel:
    user = OutUser.from_orm(orm_obj.user)
    like_users: List[OutUser] = []
    for user in orm_obj.likes:
        like_users.append(OutUser.from_orm(user))
    return Comment(
        user=user, created_at=orm_obj.created_at, text=orm_obj.text, likes=like_users
    )


@serialize.register  # type: ignore
def _(orm_obj: DB_Post) -> BaseModel:
    marked_users: List[OutUser] = []
    for user in orm_obj.marked_users:
        marked_users.append(OutUser.from_orm(user))
    comments: List[Comment] = []
    for comment in orm_obj.comments:
        comments.append(serialize(comment))
    likes = []
    for user in orm_obj.likes:
        likes.append(user)
    return Post(
        id=orm_obj.id,
        user=OutUser.from_orm(orm_obj.user),
        comments=comments,
        description=orm_obj.description,
        likes=likes,
        created_at=orm_obj.created_at,
        marked_users=marked_users,
        location=orm_obj.location,
    )


def _get_user_out_list(users: List[DB_User]) -> List[OutUser]:
    return [OutUser.from_orm(user) for user in users]


@serialize.register  # type: ignore
def _(orm_obj: DB_User) -> BaseModel:
    user_out = OutUser.from_orm(orm_obj)
    subscribers = _get_user_out_list(orm_obj.subscribers)
    subscriptions = _get_user_out_list(orm_obj.subscriptions)
    return UserInDetailOut(
        **user_out.dict(), subscriptions=subscriptions, subscribers=subscribers
    )
