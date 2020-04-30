import base64
from pathlib import Path
from typing import List, TypeVar, Union

from final_project.database.models import Post as DB_Post
from final_project.exceptions import PaginationError
from final_project.messages import Message
from final_project.models import (
    Base64,
    ImageWithPath,
    Post,
    PostWithImage,
    PostWithImagePath,
)


def rmtree(root: Path) -> None:
    for p in root.iterdir():
        if p.is_dir():
            rmtree(p)
        else:
            p.unlink()

    root.rmdir()


def decode_base64_to_bytes(base_64: Base64) -> bytes:
    return base64.standard_b64decode(base_64)


def encode_bytes_to_base64(bytes_: bytes) -> Base64:
    k = base64.standard_b64encode(bytes_)
    return Base64(k)


T = TypeVar('T')


def get_pagination(objects: List[T], page: int, size: int) -> List[T]:
    start_index: int = 0
    if page < 1 or size < 1 or page * size >= len(objects) + size:
        raise PaginationError(Message.INVALID_PAGINATION_PARAMS.value)
    if page > 1:
        start_index = (page - 1) * size
    end_index: int = start_index + size - 1
    length = len(objects)
    if end_index >= length:
        end_index = length - 1
    res: List[T] = []
    for i in range(start_index, end_index + 1):
        res.append(objects[i])
    return res


def join_posts_with_images(
    posts: List[Union[DB_Post, PostWithImagePath]], images: List[ImageWithPath]
) -> List[PostWithImage]:
    res = []
    for img in images:
        for post in posts:
            if post.image_path == img.path:
                res.append(PostWithImage(**Post.from_orm(post).dict(), image=img.image))
    return res
