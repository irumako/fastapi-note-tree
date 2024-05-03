import logging
from typing import Any

from dotenv import load_dotenv
from pydantic import (
    AnyHttpUrl,
    MongoDsn,
    SecretStr,
    field_validator,
)
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Note Service"
    DEBUG: bool = True
    LOGGING_LEVEL: int = logging.INFO
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] | str = []

    KEYCLOAK_URL: AnyHttpUrl = "http://localhost:8081/"
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT: str
    KEYCLOAK_CLIENT_SECRET: SecretStr
    KEYCLOAK_TOKEN_URL: AnyHttpUrl | None = None
    KEYCLOAK_AUTHORIZATION_URL: AnyHttpUrl | None = None

    MONGODB_URL: MongoDsn | None = None

    @field_validator("KEYCLOAK_TOKEN_URL")
    def assemble_keycloak_token(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return f"{info.data.get("KEYCLOAK_URL")}realms/{info.data.get("KEYCLOAK_REALM")}/protocol/openid-connect/token"

    @field_validator("KEYCLOAK_AUTHORIZATION_URL")
    def assemble_keycloak_auth(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        return f"{info.data.get("KEYCLOAK_URL")}realms/{info.data.get("KEYCLOAK_REALM")}/protocol/openid-connect/auth"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')


settings = Settings()
