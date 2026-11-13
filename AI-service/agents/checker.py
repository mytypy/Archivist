import asyncio
import logging

from agents.agents import agent_checker

logger = logging.getLogger(name=__name__)


async def check_model(delay: float = 3, max_attempt: int = 60) -> bool:
    """Функция для проверки прогретости модели

    Args:
        delay (float, optional): Задержка в секундах между запросами при ошибке. По умолчанию 3 секунды.
        max_attempt (int, optional): Максимальное кол-во попыток отправить запрос. По умолчанию 60 попыток.

    Returns:
        bool: True, если модель прогрелась
    """
    
    logger.info('Начинаем прогрев модели')
    logger.info(f'Задержка между запросами = {delay} секунды')
    
    message = 'Ты готов?'
    query = {'input_data': message}
    
    for attempt in range(1, max_attempt):
        logger.info(f'Попытка №{attempt}. Пробуем сделать запрос...')
        
        try:
            await agent_checker.invoke(query=query)
            logger.info('Модель прогрелась. Запускаю сервер!')
            
            return True
        except Exception as er:
            logger.error('Ошибка при запросе к модели: %s\n', er)
            
            await asyncio.sleep(delay)
            
    raise RuntimeError(f'Модель не запустилась спустя {max_attempt} попыток')