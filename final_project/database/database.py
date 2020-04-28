import asyncio
import functools
import typing
from typing import Any

from final_project.config import db_settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.util.compat import contextmanager

engine = create_engine(
    f'postgresql://{db_settings.user}:{db_settings.password}@{db_settings.server_name}/{db_settings.db_name}',
)
Base = declarative_base(bind=engine)


@contextmanager
def create_session(**kwargs: Any) -> Session:
    session = sessionmaker(bind=engine)
    new_session = session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def run_in_threadpool(
    func: typing.Callable[..., Any]
) -> typing.Callable[..., typing.Awaitable[Any]]:
    @functools.wraps(func)
    def wrap(
        *args: Any, **kwargs: Any
    ) -> typing.Coroutine[None, None, typing.Awaitable[Any]]:
        loop = asyncio.get_running_loop()

        def inner() -> typing.Awaitable[Any]:
            return func(*args, **kwargs)

        executor = loop.run_in_executor(None, inner)
        executor = typing.cast(
            typing.Coroutine[None, None, typing.Awaitable[Any]], executor
        )
        return executor

    return wrap
