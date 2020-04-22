from http import HTTPStatus

import uvicorn
from fastapi import Depends, FastAPI
from final_project.api import auth, post, posts, users
from final_project.data_access_layer.auth import check_authorization
from final_project.database.database import Base
from final_project.models import ErrorMessage


def get_app() -> FastAPI:
    Base.metadata.create_all()
    _app = FastAPI()
    _app.include_router(
        post.router,
        prefix='/users/{user_id}/posts/{post_id}',
        tags=['post'],
        dependencies=[Depends(check_authorization)],
        responses={
            HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage},
            HTTPStatus.BAD_REQUEST.value: {'model': ErrorMessage},
        },
    )
    _app.include_router(
        posts.router,
        prefix='/users/{user_id}/posts',
        tags=['posts'],
        dependencies=[Depends(check_authorization)],
        responses={
            HTTPStatus.UNAUTHORIZED.value: {'model': ErrorMessage},
            HTTPStatus.BAD_REQUEST.value: {'model': ErrorMessage},
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


app = get_app()
if __name__ == '__main__':
    uvicorn.run(app)
