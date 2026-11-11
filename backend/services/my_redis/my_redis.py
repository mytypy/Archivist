import logging
from typing import TYPE_CHECKING, Any

import redis.asyncio as aioredis

from utils.config.configs import get_redis_settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    class BaseRedis(aioredis.Redis):
        """Класс для подсказок в IDE"""
else:
    class BaseRedis:
        """Класс для затычки в runtime"""
    
    
class Redis(BaseRedis):
    """Класс для разных взаимодействий с Redis"""
    
    def __init__(self):
        redis_settings = get_redis_settings()
        self.redis: aioredis.Redis = aioredis.Redis(host=redis_settings.HOST, port=redis_settings.PORT, decode_responses=True)

    async def ping(self, retries_for_ping: int = 10) -> None:
        """Функция для проверки состояния redis сервера

        Args:
            retries_for_ping (int, optional): Кол-во попыток для пинга. По умолчанию 10.

        Raises:
            RuntimeError: Исключение, если не получен ответ от сервиса
        """
        for i in range(1, retries_for_ping + 1):
            logger.info(f"Пробуем подключиться к Redis. Попытка №{i}")
            
            try:
                await self.redis.ping()
                
                break
            except Exception as er:  # noqa: BLE001
                logger.error(f'Не удалось подключиться к Redis: {er}')
        else:
            raise RuntimeError('Не удалось подключиться к Redis')
        
    async def init(self, retries_for_ping: int = 10) -> None:
        """Функция для инициализации Redis клиента

        Args:
            retries_for_ping (int, optional): Кол-во попыток для пинга Redis

        Raises:
            RuntimeError: Исключение, если не удалось пингануть Redis спустя retries_for_ping попыток
        """
        
        await self.ping(retries_for_ping=retries_for_ping)
        
        logger.info('Успешно подключились к Redis!')
    
    async def close(self) -> None:
        """Функция для закрытия соединения Redis"""
        
        await self.redis.aclose()
    
    def __getattr__(self, name: str) -> Any:
        """
        Магический(dunder) метод для получения аттрибута, которого нет в классе
        (нужен для использования в сочетании с наследованием)

        Args:
            name (str): Имя аттрибута

        Returns:
            Any: Объект класса aioredis.Redis
        """
        
        return getattr(self.redis, name)


redis = Redis()


async def get_redis() -> aioredis.Redis:
    """Функция для получения объекта redis

    Returns:
        aioredis.Redis: Объект класса aioredis.Redis
    """
    
    return redis.redis