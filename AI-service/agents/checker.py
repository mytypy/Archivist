import asyncio
import logging

from agents.agent import Agent
from constants.settings import MODEL
from schemas.model.model import (
    SimpleResponse,
)

logger = logging.getLogger(name=__name__)


async def check_model(delay: float = 3.0) -> bool:
    """Функция для проверки прогретости модели

    Args:
        delay (float, optional): Задержка между запросами при ошибке. По умолчанию 3.0.

    Returns:
        bool: True, если модель прогрелась
    """
    
    logger.info('Начинаем прогрев модели')
    
    agent = Agent(model_name=MODEL,
        system_prompt='',
        pydantic_object=SimpleResponse,
        temperature=0.1)
    
    message = 'Ты готов?'
    query = {'input_data': message}
    
    while True:
        logger.info('Пробуем сделать запрос...')
        
        try:
            await agent.invoke(query=query)
            logger.info('Модель прогрелась! Запускаю сервер!')
            
            return True
        except Exception as er:
            logger.error('Ошибка при запросе к модели: %s\n', er)
            await asyncio.sleep(delay)