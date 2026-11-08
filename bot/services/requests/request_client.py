import logging

import aiohttp


class RequestModule:
    """Класс для различных взаимодействий с aiohttp
    """
    
    def __init__(self, *args, **settings):
        self.args = args
        self.kwargs = settings
        self.logger = logging.getLogger(__name__)
    
    async def __test_connection(self, retries: int = 10) -> None:
        """Функция для тестового запроса к 8.8.8.8

        Args:
            retries (int, optional): Кол-во попыток для запроса к 8.8.8.8

        Raises:
            RuntimeError: Ошибка, если неудалось сделать запрос к 8.8.8.8 спустя retries попыток
        """
        
        for i in range(1, retries + 1):
            try:
                async with self.session.get('https://8.8.8.8/') as response:
                    self.logger.info(f'Попытка №{i}. Пробуем сделать запрос к 8.8.8.8')
                    self.logger.info(f'Статус запроса к 8.8.8.8: {response.status}')
                            
            except Exception as er:  # noqa: BLE001
                self.logger.error(f'Что-то не так с запросом к 8.8.8.8: {er}')
            else:
                return
                    
        raise RuntimeError('Что-то не так с запросом к 8.8.8.8')
        
    async def init(self, retries: int = 10) -> None:
        """Функция для инициализации aiohttp сессии

        Args:
            retries (int, optional): Кол-во попыток для запроса к 8.8.8.8
        """
        
        self.session = aiohttp.ClientSession(*self.args, **self.kwargs)
        await self.__test_connection(retries=retries)
    
    
    async def close(self) -> bool:
        """Функция для закрытия сессии"""
        if self.session.closed is False:
            await self.session.close()
        
        return True
        
        
timeout = aiohttp.ClientTimeout(total=120)
request = RequestModule(trust_env=True, timeout=timeout)