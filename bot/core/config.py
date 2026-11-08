from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = '../.env'


class BotSettings(BaseSettings):
    TOKEN: str
    SECRET_TOKEN: str
    SECRET_HEADER: str
    BACKEND_URL: str
    
    NGROK_TOKEN: str
    NGROK_URL: str
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_prefix='BOT_',
        extra='ignore'
    )