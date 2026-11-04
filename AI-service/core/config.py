from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = './.env'


class AppSettings(BaseSettings):
    MODEL_URL: str
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra='ignore',
        env_prefix='AI_SERVICE_'
    )