from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = Field(default="development", alias="ENVIRONMENT")
    mongo_url: str = Field(default="mongodb://localhost:27017", alias="MONGO_URL")
    database_name: str = Field(default="jlc_db", alias="DATABASE_NAME")
    redis_url: Optional[str] = Field(default=None, alias="REDIS_URL")

    rate_limit_requests_per_minute: int = Field(
        default=60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    rate_limit_window_seconds: int = Field(
        default=60, alias="RATE_LIMIT_WINDOW_SECONDS"
    )
    api_client_timeout_seconds: float = Field(
        default=10.0, alias="API_CLIENT_TIMEOUT_SECONDS"
    )
    api_client_connect_timeout_seconds: float = Field(
        default=5.0, alias="API_CLIENT_CONNECT_TIMEOUT_SECONDS"
    )

    auth_service_url: str = Field(default="http://localhost:8000", alias="AUTH_SERVICE_URL")
    base_url: str = Field(default="http://localhost:8001", alias="BASE_URL")
    upload_dir: Path = Field(default=Path("/app/uploads"), alias="UPLOAD_DIR")

    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS",
    )

    smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, alias="SMTP_PORT")
    smtp_username: str = Field(
        default="",
        validation_alias=AliasChoices("SMTP_USERNAME", "SMTP_USER"),
    )
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    from_email: str = Field(default="noreply@jlcgroup.com", alias="FROM_EMAIL")
    from_name: str = Field(default="JLC Group", alias="FROM_NAME")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):  # type: ignore[override]
        if value is None:
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("upload_dir", mode="after")
    @classmethod
    def ensure_upload_dir(cls, value: Path) -> Path:
        return value.expanduser()


def get_settings() -> Settings:
    return _get_settings_cached()


@lru_cache()
def _get_settings_cached() -> Settings:
    return Settings()
