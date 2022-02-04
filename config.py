from os import environ

from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")


class BaseConfig:
    """
    Базовая конфигурация приложения
    """
    DB_NAME: str = environ.get("DB_NAME", 'delete')
    DB_USER: str = environ.get("DB_USER", 'delete')
    DB_PASSWORD: str = environ.get("DB_PASSWORD", 'delete')
    DB_HOST: str = "postgresql"
    DB_PORT: int = int(environ.get("DB_PORT", 'delete'))

    # jwt
    JWT_SECRET_KEY: str = environ.get("JWT_SECRET_KEY", "delete")
    JWT_EXPIRE: float = float(environ.get("JWT_EXPIRE", "delete"))  # min
    JWT_ALGORITHM: str = "HS256"

    @property
    def SQLALCHEMY_DB_URI(self):
        uri: str = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return uri


__conf: dict = {
    "local": BaseConfig
}


def get_config() -> BaseConfig:
    current_conf: BaseConfig = __conf[environ.get("CUR_ENV", 'local')]()
    return current_conf
