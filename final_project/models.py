import re
from datetime import datetime
from typing import Any, Callable, Iterable, List, Optional

from final_project.messages import Message
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


class Base64(bytes):
    @classmethod
    def __get_validators__(cls) -> Iterable[Callable[[Any], bytes]]:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> bytes:
        if isinstance(value, bytes):
            value = value.decode()
        if value is None or not isinstance(value, str):
            raise ValueError(f'actual value type is {type(value)} but expected{str}',)
        if len(value) % 4 != 0:
            raise ValueError(Message.INVALID_BASE64_PADDING.value)
        pattern = re.compile('^[A-Za-z0-9+/]+={0,2}$')
        if not re.match(pattern, value):
            raise ValueError('value is not in byte64 format')
        return value.encode()


class Like(BaseModel):
    user: OutUser


class Comment(BaseModel):
    user: OutUser
    created_at: datetime
    text: str
    likes: List[Like]


class Post(BaseModel):
    user: OutUser
    comments: List[Comment]
    description: Optional[str] = None
    likes: List[Like]
    created_at: datetime
    marked_users: List[OutUser]
    location: Optional[str] = None


class PostWithImage(Post):
    image: Base64


class TaskResponse(BaseModel):
    status: str
    task_id: str
    post_id: Optional[int] = None
    error_text: Optional[str] = None


class InPost(BaseModel):
    image: Base64
    description: str
    marked_users_ids: Optional[List[int]] = None
    location: Optional[str] = None


class WorkerResult(BaseModel):
    post_id: Optional[int] = None
    error: Optional[str] = None


class Image(BaseModel):
    image: Base64


class ImageWithPath(Image):
    path: str
