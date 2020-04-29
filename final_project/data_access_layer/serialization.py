from functools import singledispatch
from typing import List

from final_project.database.database import Base
from final_project.database.models import Comment as DB_Comment
from final_project.database.models import Post as DB_Post
from final_project.models import Comment, OutUser, Post
from pydantic import BaseModel


@singledispatch
def serialize(orm_obj: Base) -> BaseModel:
    raise ValueError()


@serialize.register
def _(orm_obj: DB_Comment) -> BaseModel:
    user_id = orm_obj.user_id
    user = OutUser.from_orm(orm_obj.user)
    like_users: List[OutUser] = []
    for user in orm_obj.likes:
        like_users.append(OutUser.from_orm(user))
    return Comment(
        user=user, created_at=orm_obj.created_at, text=orm_obj.text, likes=like_users
    )


@serialize.register
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
        user=OutUser.from_orm(orm_obj.user),
        comments=comments,
        description=orm_obj.description,
        likes=likes,
        created_at=orm_obj.created_at,
        marked_users=marked_users,
        location=orm_obj.location,
    )
