from http import HTTPStatus

from fastapi import HTTPException


def check_user(user_id_expected: int, user_id_actual: int) -> None:
    if user_id_expected != user_id_actual:
        raise HTTPException(HTTPStatus.FORBIDDEN.value)
