class UsersDALError(Exception):
    pass


class UsersDALDoesNotExistsError(Exception):
    pass


class AuthDALError(Exception):
    pass


class PostsDALError(Exception):
    pass


class MyImageError(Exception):
    pass


class PostsDALNotExistsError(Exception):
    pass


class PostDALNotExistsError(Exception):
    pass


class StorageDALNotExistsError(Exception):
    pass


class StorageClientError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code: int = status_code


class StorageError(Exception):
    pass


class PostDALError(Exception):
    pass
