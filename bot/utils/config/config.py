from functools import lru_cache

from core.config import BotSettings


@lru_cache
def get_bot_settings() -> BotSettings:
    """Функция для получения настроек бота и сохранения их в кэш

    Returns:
        BotSettings: Экземпляр класса
    """
    
    return BotSettings()