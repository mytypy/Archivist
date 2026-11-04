import asyncio
import logging

from core.config import AppSettings
from services.requests.request_client import request

logger = logging.getLogger(name=__name__)


async def check_llm_service(delay: float = 3.0) -> bool:
    """Функция для проверки сервиса llm-service

    Args:
        delay (float): Задержка между запросами после ошибок

    Returns:
        bool: True, если все хорошо
    """
    settings = AppSettings()
    URL = f'{settings.AI_SERVICE_URL}/health/'
    
    logger.info('Проверяем llm-service...')
    
    while True:
        try:
            async with request.session.get(URL) as response:
                if response.ok:
                    logger.info('Сервис запущен. Запускаю сервер бекенда')
                    
                    return True
                
        except Exception as er:
            logger.error('Ошибка при запросе к llm-service: %s\nПробуем еще раз', str(er))
            await asyncio.sleep(delay)