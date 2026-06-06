from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_env: str = Field(default='development', alias='APP_ENV')
    cors_origins: str = Field(default='http://localhost:5173', alias='CORS_ORIGINS')


settings = Settings()
