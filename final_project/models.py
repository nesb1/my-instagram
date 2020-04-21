from datetime import datetime
from typing import Any, List

from pydantic import BaseModel


class UserId(BaseModel):
    user_id: int


class UserCommon(BaseModel):
    username: str


class InUser(UserCommon):
    password: str


class OutUser(UserCommon):
    id: int

    class Config:
        orm_mode = True


class ErrorMessage(BaseModel):
    message: str


class TokensResponse(BaseModel):
    token_type: str
    access_token: bytes
    refresh_token: bytes

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TokensResponse):
            return True
        return (
            self.access_token == other.access_token
            and self.refresh_token == other.refresh_token
        )


class FreshTokenInput(BaseModel):
    token: str


class Like(BaseModel):
    user: OutUser


class Comment(BaseModel):
    user: OutUser
    created_at: datetime
    text: str
    likes: List[Like]


class Post(BaseModel):
    user: OutUser
    image: str  # base64
    comments: List[Comment]
    description: str
    likes: List[Like]
    created_at: datetime
    marked_users: List[OutUser]
    location: str


class InPost(BaseModel):
    user_id: int
    image: str  # base 64
    description: str
    marked_users_ids: List[int]
    location: str
