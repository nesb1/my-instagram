from pydantic import BaseSettings


class TokensSettings(BaseSettings):
    access_token_expire_minutes = 15
    refresh_toke_expire_time_days = 7
    token_type = 'bearer'


tokens_settings = TokensSettings()
