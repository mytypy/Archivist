from functools import lru_cache

from core.config import AppSettings, DatabaseSettings, RedisSettings


@lru_cache
def get_db_settings() -> DatabaseSettings:
    """Функция для получения настроек БД из env и сохранения результата в кэш

    Returns:
        DatabaseSettings: Экземпляр класса
    """
    
    return DatabaseSettings()


@lru_cache
def get_app_settings() -> AppSettings:
    """Функция для получения настроек приложения из env и сохранения результата в кэш
    
    Returns:
        AppSettings: Экземпляр класса
    """
    
    return AppSettings()


@lru_cache
def get_redis_settings() -> RedisSettings:
    """Функция для получения настроек redis из env и сохранения результата в кэш
        
    Returns:
        RedisSettings: Экземпляр класса
    """
        
    return RedisSettings()