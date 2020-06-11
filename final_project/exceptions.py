from fastapi import HTTPException


class DALError(HTTPException):
    pass


class StorageClientError(Exception):
    pass


class MyImageError(Exception):
    pass


class StorageError(Exception):
    pass


class PaginationError(Exception):
    pass
