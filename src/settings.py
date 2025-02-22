from typing import Type
import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_settings(cls: Type[BaseSettings]) -> BaseSettings:
    dotenv.load_dotenv()
    return cls()


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="database_")

    driver: str = "postgresql"
    async_driver: str = "postgresql+asyncpg"
    name: str
    username: str
    password: str
    host: str

    @property
    def url(self) -> str:
        return (
            f"{self.driver}://{self.username}:{self.password}@{self.host}/{self.name}"
        )

    @property
    def async_url(self) -> str:
        return f"{self.async_driver}://{self.username}:{self.password}@{self.host}/{self.name}"
