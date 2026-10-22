from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = '../.env'


class DatabaseSettings(BaseSettings):
    """Класс для получения данных для БД"""
    
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DB: str
    
    PG_BOUNCER_PORT: int
    PG_BOUNCER_HOST: str

    model_config = SettingsConfigDict(
        env_prefix='POSTGRES_',
        env_file=ENV_FILE_PATH,
        extra='ignore'
        )


class RedisSettings(BaseSettings):
    """Класс для получения данные для Redis"""
    
    HOST: str
    PORT: int
    
    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
        env_file=ENV_FILE_PATH,
        extra='ignore'
        )


class AppSettings(BaseSettings):
    """Класс для получения данных приложения"""
    
    SECRET_TOKEN: str
    SECRET_HEADER: str
    
    model_config = SettingsConfigDict(
            env_prefix='APP_',
            env_file=ENV_FILE_PATH,
            extra='ignore'
            )