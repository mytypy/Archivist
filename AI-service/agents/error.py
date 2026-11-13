import asyncio
import logging

from fastapi import HTTPException, status
from pydantic import BaseModel

from agents.agent import Agent

logger = logging.getLogger(name=__name__)


async def ai_retries(max_retries: int, agent: Agent, error_msg: str, data_for_agent: dict) -> BaseModel:
    """Функция-обертка для обработки ошибок при запросах

    Args:
        max_retries (int): Максимальное кол-во попыток отправить запроса
        agent (Agent): Объект агента
        error_msg (str): Сообщение с ошибкой, которое вернется и выведется
        data_for_agent (dict): Данные для агента
    
    Raises:
        HTTPException: Исключение, если модель не выдала нормльный ответ после max_retries

    Returns:
        BaseModel: Объект BaseModel
    """
    
    error = None
    
    try:
        result = await agent.invoke(data_for_agent)
    except Exception as er:
        logger.error('\n Получили ошибку при запросе к модели: %s. Error: %s', error_msg, str(er))
        counter = 1
            
        while counter <= max_retries:
            try:
                logger.info('Попытка № %s', counter)
                await asyncio.sleep(1)
                
                result = await agent.invoke(data_for_agent)
                return result
            
            except Exception as er:
                counter += 1
                error = er
                logger.error('Получили ошибку при запросе к модели: %s.\n', str(error))
            
        raise HTTPException(detail=error_msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return result