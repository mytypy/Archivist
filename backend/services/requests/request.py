import asyncio
import datetime
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


async def request_to_validate_chat_message(message: str, date_send: datetime.datetime) -> str | dict:
    settings = AppSettings()
    URL = f'{settings.AI_SERVICE_URL}/api/model/validate-chat-message/'

    data = {
        'message': message,
        'date_send': str(date_send)
    }

    logger.info('Отправили запрос на валидацию сообщения из чата...')

    try:
        async with request.session.post(URL, json=data) as responce:
            validation_responce = await responce.json()
            result: str | dict = validation_responce["responce"]

            return result

    except Exception as err:
        logger.error('Ошибка при валидации сообщения: %s', str(err))
        return "Ошибка при валидации сообщения. Попробуйте позже."


async def request_to_validate_user_question(question: str) -> str | dict:
    settings = AppSettings()
    URL = f'{settings.AI_SERVICE_URL}/api/model/validate-question/'

    data = {
        'question': question
    }

    logger.info('Отправили запрос на валидацию вопроса пользователя...')

    try:
        async with request.session.post(URL, json=data) as responce:
            validation_responce = await responce.json()
            result: str | dict = validation_responce["responce"]

            return result

    except Exception as err:
        logger.error('Ошибка при валидации вопроса: %s', str(err))
        return "Ошибка при валидации вопроса. Попробуйте позже."


async def request_to_get_filters(message: str, date_send: datetime.datetime) -> str | dict:
    settings = AppSettings()
    URL = f'{settings.AI_SERVICE_URL}/api/model/get-filters/'

    data = {
        'message': message,
        'date_send': date_send
    }

    logger.info('Отправили запрос на получение фильтров...')

    try:
        async with request.session.post(URL, json=data) as responce:
            validation_responce = await responce.json()
            result: str | dict = validation_responce["responce"]

            return result

    except Exception as err:
        logger.error('Ошибка при получении фильтров: %s', str(err))
        return "Ошибка при получении фильтров. Попробуйте позже."