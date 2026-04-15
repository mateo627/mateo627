from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="mateo627")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    database_url: str = Field(default="sqlite+pysqlite:///./data/app.db")
    jwt_secret_key: str = Field(default="insecure-change-me")
    access_token_expire_minutes: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
