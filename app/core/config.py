from functools import lru_cache
from typing import List

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Stock Prediction & Trading Signals API"
    mongo_uri: AnyUrl = Field("mongodb://mongo:27017", validation_alias="MONGO_URI")
    mongo_db_name: str = Field("stock_signals", validation_alias="MONGO_DB_NAME")

    jwt_secret_key: str = Field("devsecret", validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(60 * 24 * 7, validation_alias="REFRESH_TOKEN_EXPIRE_MINUTES")

    allowed_origins: List[str] = Field(default_factory=lambda: ["*"], validation_alias="ALLOWED_ORIGINS")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
