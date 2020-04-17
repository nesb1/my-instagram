import asyncio
import functools
import pathlib
import typing
from typing import Any

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.util.compat import contextmanager

cur_path = (pathlib.Path().parent.parent / 'my.db').resolve()
DB_URL = 'sqlite:////' + str(cur_path)
engine = sa.create_engine(DB_URL)

Base = declarative_base(bind=engine)


def fk_pragma_on_connect(dbapi_con: Any, con_record: Any) -> None:
    # pylint: disable=unused-argument
    dbapi_con.execute('pragma foreign_keys=ON')


event.listen(engine, 'connect', fk_pragma_on_connect)


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
