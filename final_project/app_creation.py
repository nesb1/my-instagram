from http import HTTPStatus

from fastapi import FastAPI
from final_project.api import auth, post, posts, users
from final_project.models import ErrorMessage


def get_app() -> FastAPI:
    _app = FastAPI()
    _app.include_router(
        post.router,
        prefix='/users/{user_id}/posts/{post_id}',
        tags=['post'],
        responses={
            HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage},
            HTTPStatus.BAD_REQUEST.value: {'model': ErrorMessage},
        },
    )
    _app.include_router(
        posts.router,
        prefix='/users/{user_id}/posts',
        tags=['posts'],
        responses={
            HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage},
            HTTPStatus.BAD_REQUEST.value: {'model': ErrorMessage},
            HTTPStatus.NOT_FOUND.value: {'model': ErrorMessage},
        },
    )
    _app.include_router(
        users.router,
        prefix='/users',
        tags=['users'],
        responses={HTTPStatus.BAD_REQUEST.value: {'model': ErrorMessage}},
    )
    _app.include_router(
        auth.router,
        prefix='/auth',
        tags=['auth'],
        responses={HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage}},
    )
    return _app
