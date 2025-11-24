from functools import lru_cache
from typing import List, Union

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Stock Prediction & Trading Signals API"
    mongo_uri: AnyUrl = Field("mongodb+srv://Ibrahim_Hamdan_db:Ibr@him1912@cluster0.ayr8ym4.mongodb.net/", validation_alias="MONGO_URI")
    mongo_db_name: str = Field("stock_signals", validation_alias="MONGO_DB_NAME")

    jwt_secret_key: str = Field("devsecret", validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(60 * 24 * 7, validation_alias="REFRESH_TOKEN_EXPIRE_MINUTES")

    # Email settings (for production)
    frontend_url: str = Field("http://localhost:3000", validation_alias="FRONTEND_URL")
    smtp_host: str = Field("smtp.gmail.com", validation_alias="SMTP_HOST")
    smtp_port: int = Field(587, validation_alias="SMTP_PORT")
    smtp_user: str = Field("", validation_alias="SMTP_USER")
    smtp_password: str = Field("", validation_alias="SMTP_PASSWORD")
    email_from: str = Field("noreply@stockpredict.com", validation_alias="EMAIL_FROM")

    allowed_origins: str = Field(default="*", validation_alias="ALLOWED_ORIGINS")

    def get_allowed_origins(self) -> List[str]:
        """Parse allowed origins from string to list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
