
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    class Config:
        env_file = ".env"
        extra = "allow"


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = "sqlite+aiosqlite:///./test.db"
    BD_FORCE_ROLLBACK: bool = False


class DevConfig(GlobalConfig):
    class Config:
        env_prefix: str = "DEV_"
        extra = "allow"

class ProdConfig(GlobalConfig):
    class Config:
        env_prefix: str = "PROD_"
        extra = "allow"


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test.db"

    # match the field name used in GlobalConfig (BD_FORCE_ROLLBACK)
    BD_FORCE_ROLLBACK: bool = True

    class Config:
        env_prefix: str = "TEST_"
        extra = "allow"


@lru_cache()
def get_config(env_state: str):
    configs ={"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state.lower()]()

# Handle None ENV_STATE by defaulting to 'test' for tests
env_state = BaseConfig().ENV_STATE or "test"
config = get_config(env_state)