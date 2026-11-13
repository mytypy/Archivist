from functools import lru_cache

from core.config import AppSettings


@lru_cache
def get_app_settings() -> AppSettings:
    """Функция для получения настроек приложения из env и сохранения результата в кэш
    
    Returns:
        AppSettings: Экземпляр класса
    """
    
    return AppSettings()