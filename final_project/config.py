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


app_settings = AppSettings()
tokens_settings = TokensSettings()
logging_settings = LoggingSettings()
