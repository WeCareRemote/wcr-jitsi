import secrets
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union
import os
from pydantic import field_validator
from pydantic_settings import BaseSettings as PydanticSettings

BASE_DIRECTORY = Path(__file__).parent.parent.parent


class BaseSettings(PydanticSettings):
    reload: bool = False
    DEBUG: bool = False
    API_DISABLE_DOCS: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALLOW_ORIGINS: Union[str, list[str]] = None
    RECORDS_HANDLER_TOKEN: str
    RECORDS_DIR: str
    S3_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    PRESIGNED_URL_EXPIRES_IN: int = 3600
    STORAGE_HOST: str
    GREYT_HOST: str
    DB_HOST: str
    DB_PORT: str = None
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("ALLOW_ORIGINS", mode="before")
    @classmethod
    def assemble_origins(cls, v: Optional[str]) -> list[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return ["*"]

    @field_validator("STORAGE_HOST", mode="before")
    @classmethod
    def prepare_storage_host(cls, v: str) -> str:
        return v[:-1] if v.endswith("/") else v

    @field_validator("GREYT_HOST", mode="before")
    @classmethod
    def prepare_greyt_host(cls, v: str) -> str:
        return v[:-1] if v.endswith("/") else v

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        user = values.get("DB_USERNAME")
        password = values.get("DB_PASSWORD")
        host = values.get("DB_HOST")
        port = values.get("DB_PORT") or "3307"
        db = values.get("DB_DATABASE")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

    def get_fast_api_init_keys(self) -> dict:
        return {
            k: v
            for k, v in self.model_dump().items()
            if k.lower() in ("api_disable_docs", "debug")
        }

    def get_uvicorn_init_keys(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if k.lower() in ["reload"]}


class DevelopmentSettings(BaseSettings):
    reload: bool = True
    DEBUG: bool = True


class ProductionSettings(BaseSettings):
    API_DISABLE_DOCS: bool = True


@lru_cache()
def get_settings() -> BaseSettings:
    app_mode = os.environ.get("APP_MODE", "production")
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
    }
    return settings_map[app_mode]()


settings = get_settings()
