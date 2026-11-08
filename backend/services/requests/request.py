import asyncio
import datetime
import logging

from services.requests.request_client import request
from utils.config.configs import get_app_settings

logger = logging.getLogger(name=__name__)


async def check_llm_service(delay: float = 3.0) -> bool:
    """Функция для проверки сервиса llm-service

    Args:
        delay (float): Задержка между запросами после ошибок

    Returns:
        bool: True, если все хорошо
    """
    settings = get_app_settings()
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
    """Функция для запроса на валидацию сообщения из чата

    Args:
        message (str): Сообщение
        date_send (datetime.datetime): Дата отправки

    Returns:
        str | dict: Текст ошибки или нормальный результат
    """
    
    settings = get_app_settings()
    
    URL = f'{settings.AI_SERVICE_URL}/api/model/validate-chat-message/'

    data = {
        'message': message,
        'date_send': str(date_send)
    }

    logger.info('Отправили запрос на валидацию сообщения из чата...')

    try:
        async with request.session.post(URL, json=data) as responce:
            validation_responce = await responce.json()
            logger.info(validation_responce)
            
            result: str | dict = validation_responce["response"]

            return result

    except Exception as err:
        logger.exception('Ошибка при валидации сообщения:')
        return "Ошибка при валидации сообщения. Попробуйте позже."


async def request_to_validate_user_question(question: str) -> str | dict:
    """Функция для отправки запроса на валидацию вопроса пользователя

    Args:
        question (str): Вопрос пользователя

    Returns:
        str | dict: Текст ошибки или нормальный результат
    """
    settings = get_app_settings()
    
    URL = f'{settings.AI_SERVICE_URL}/api/model/validate-question/'

    data = {
        'question': question
    }

    logger.info('Отправили запрос на валидацию вопроса пользователя...')

    try:
        async with request.session.post(URL, json=data) as responce:
            validation_responce = await responce.json()
            logger.info(validation_responce)
            result: str | dict = validation_responce["response"]

            return result

    except Exception as err:
        logger.error('Ошибка при валидации вопроса: %s', str(err))
        return "Ошибка при валидации вопроса. Попробуйте позже."


async def request_to_get_filters(question: str, date_send: str) -> str | dict:
    """Функция для отправки запроса на получение фильтров

    Args:
        question (str): Вопрос пользователя
        date_send (str): Дата отправки сообщения

    Returns:
        str | dict: Текст ошибки или нормальный результат
    """
    
    settings = get_app_settings()
    
    URL = f'{settings.AI_SERVICE_URL}/api/model/get-filters/'

    data = {
        'question': question,
        'date_send': date_send
    }

    logger.info('Отправили запрос на получение фильтров...')

    try:
        async with request.session.post(URL, json=data) as responce:
            validation_responce = await responce.json()
            logger.info(validation_responce)
            result: str | dict = validation_responce["response"]

            return result

    except Exception as err:
        logger.error('Ошибка при получении фильтров: %s', str(err))
        return "Ошибка при получении фильтров. Попробуйте позже."


async def request_to_finally_request(user_question: str, date_send: datetime.datetime,
                                     chat_messages: list[dict], date_range_start: datetime.datetime,
                                     date_range_end: datetime.datetime) -> str | dict:
    """Функция для отправки запроса на получение финального ответа от агента

    Args:
        user_question (str): Вопрос пользователя
        date_send (datetime.datetime): Дата отправки сообщения
        chat_messages (list[dict]): Сообщения из чата
        date_range_start (datetime.datetime): Дата начала интервала n дней назад от даты, которая интересует пользователя
        date_range_end (datetime.datetime): Дата окончания интервала

    Returns:
        str | dict: Текст ошибки или нормальный результат
    """
    settings = get_app_settings()
    
    URL = f'{settings.AI_SERVICE_URL}/api/model/get-answer/'

    data = {
        'user_question': user_question,
        'date_send': date_send,
        'chat_messages': chat_messages,
        'date_range_start': date_range_start,
        'date_range_end': date_range_end
    }

    logger.info('Отправили запрос на получение ДЗ...')

    try:
        async with request.session.post(URL, json=data) as responce:
            validation_responce = await responce.json()
            logger.info(validation_responce)
            result: str | dict = validation_responce["response"]

            return result

    except Exception as err:
        logger.error('Ошибка при получении ДЗ: %s', str(err))
        
        return "Ошибка при получении ДЗ. Попробуйте позже."