from enum import Enum


class Message(Enum):
    USER_ALREADY_EXISTS = 'User already exists'
    USER_DOES_NOT_EXISTS = 'User does not exists'
    COULD_NOT_VALIDATE_CREDENTIALS = 'Could not validate credentials'
    NOT_EXPECTING_PAYLOAD = 'Not expecting payload'
    ACCESS_TOKEN_OUTDATED = 'Access token outdated'
    INCORRECT_USERNAME_OR_PASSWORD = 'Incorrect username or password'
    INVALID_REFRESH_TOKEN = 'Invalid refresh token'
