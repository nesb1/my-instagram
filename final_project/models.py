from typing import Any

from pydantic import BaseModel


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
