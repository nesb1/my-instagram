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
