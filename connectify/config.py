from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    model_config = SettingsConfigDict(env_file="connectify/.env", extra="ignore")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLLBACK: Optional[bool] = False


class DevelopmentConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestingConfig(GlobalConfig):
    DATABASE_URL: Optional[str] = "sqlite:///./test.db"
    DB_FORCE_ROLLBACK: Optional[bool] = True


class ProductionConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


@lru_cache()
def get_config(ENV_STATE) -> GlobalConfig:
    configs = {
        "dev": DevelopmentConfig,
        "test": TestingConfig,
        "prod": ProductionConfig,
    }
    return configs[ENV_STATE]()


config: GlobalConfig = get_config(BaseConfig().ENV_STATE)
