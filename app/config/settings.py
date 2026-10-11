from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = "Selamber Community"
    debug: bool = True
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./selamber.db"
    bot_token: str = ""
    admin_chat_id: str = ""
    admin_api_token: str = ""
    allowed_hosts: str = "localhost,127.0.0.1"


settings = Settings()
