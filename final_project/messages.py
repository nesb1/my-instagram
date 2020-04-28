from enum import Enum


class Message(Enum):
    USER_ALREADY_EXISTS = 'User already exists'
    USER_DOES_NOT_EXISTS = 'User does not exists'
    COULD_NOT_VALIDATE_CREDENTIALS = 'Could not validate credentials'
    NOT_EXPECTING_PAYLOAD = 'Not expecting payload'
    ACCESS_TOKEN_OUTDATED = 'Access token outdated'
    INCORRECT_USERNAME_OR_PASSWORD = 'Incorrect username or password'
    INVALID_REFRESH_TOKEN = 'Invalid refresh token'
    INVALID_IMAGE = 'Invalid image'
    INCORRECTLY_MARKED_USERS = 'Nonexistent user is marked or one user repeated multiple times or marked himself'
    POST_ACCEPTED_FOR_PROCESSING = 'Post accepted for processing'
    POST_READY = 'Post ready'
    POST_TASK_FALLEN = 'Post task fallen'
    ACCESS_FORBIDDEN = 'access_forbidden'
    BYTES_ARE_NOT_A_IMAGE = 'Bytes are not a image'
    INVALID_BASE64_PADDING = 'Invalid base64 padding'
    TASK_NOT_EXISTS = 'Task not exists'
