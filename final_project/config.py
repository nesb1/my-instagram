import logging

from pydantic import BaseSettings


class TokensSettings(BaseSettings):
    access_token_expire_minutes = 15
    refresh_toke_expire_time_days = 7
    token_type = 'bearer'


class LoggingSettings(BaseSettings):
    level = logging.INFO
    file_name = 'logs.log'


class AppSettings(BaseSettings):
    name = 'todo'


class ImageStorageSettings(BaseSettings):
    items_in_one_folder = 1000
    storage_folder_name = 'image-storage'
    address: str = 'storage'
    port: int = 8001
    image_format: str = 'png'


class ImageCuttingSettings(BaseSettings):
    aspect_resolution = 10


class RedisSettings(BaseSettings):
    redis_address = 'redis'


class DataBaseSettings(BaseSettings):
    server_name = 'db'
    user = 'evgeny'
    password = '5211'
    db_name = 'database'


db_settings = DataBaseSettings()
redis_settings = RedisSettings()
image_cutting_settings = ImageCuttingSettings()
image_storage_settings = ImageStorageSettings()
app_settings = AppSettings()
tokens_settings = TokensSettings()
logging_settings = LoggingSettings()
