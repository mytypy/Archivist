import asyncio
import logging

from services.requests.request_client import request
from utils.config.config import get_bot_settings

logger = logging.getLogger(name=__name__)


async def check_backend_service(delay: float = 3.0) -> bool:
    """Функция для проверки сервиса llm-service

    Args:
        delay (float): Задержка между запросами после ошибок

    Returns:
        bool: True, если все хорошо
    """
    settings = get_bot_settings()
    URL = f'{settings.BACKEND_URL}/health/'
    
    logger.info('Проверяем backend...')
    
    while True:
        try:
            async with request.session.get(URL) as response:
                if response.ok:
                    logger.info('Сервис запущен. Запускаю бота')
                    
                    return True
                
        except Exception as er:
            logger.error('Ошибка при запросе к backend: %s\nПробуем еще раз', str(er))
            await asyncio.sleep(delay)
            
            
async def request_to_add_users(members_id: list[int], chat_id: int, chat_title: str) -> str | dict:
    settings = get_bot_settings()
    
    URL = f'{settings.BACKEND_URL}/api/user/set-user/'

    data = {
        'user_ids': members_id,
        'chat_id': chat_id,
        'chat_title': chat_title
    }

    logger.info('Отправили запрос на добавление пользователей в БД...')

    try:
        async with request.session.post(URL, json=data) as responce:
            responce = await responce.json()
            result: str | None = responce.get('response')
            
            if result is None:
                result = responce.get('detail')
            else:
                result = responce

            return result

    except Exception:
        logger.exception('Ошибка при добавлении пользователей')
        
        return "Ошибка при добавлении пользователей. Попробуйте позже."


async def send_message_to_server(message: str, user_id: int, chat_title: str, chat_id: int, date_send: str) -> str | dict:
    settings = get_bot_settings()
    
    URL = f'{settings.BACKEND_URL}/api/message/add-message/'

    data = {
        'text': message,
        'max_id': user_id,
        'chat_id': chat_id,
        'timestamp': date_send,
        'chat_title': chat_title
    }

    logger.info('Отправили запрос на добавление сообщения в БД...')

    try:
        async with request.session.post(URL, json=data) as responce:
            responce = await responce.json()
            result: str | None = responce.get('response')
            
            if result is None:
                result = responce.get('detail')

            return result

    except Exception:
        logger.exception('Ошибка при добавлении сообщения')
        
        return "Ошибка при добавлении сообщения. Попробуйте позже."
    

async def get_user_chats_from_db(max_user_id: int) -> str | dict:
    settings = get_bot_settings()
    
    URL = f'{settings.BACKEND_URL}/api/user/get-user-chats/{max_user_id}'

    logger.info('Отправили запрос на получение чатов из БД...')

    try:
        async with request.session.get(URL) as responce:
            responce = await responce.json()
            
            if isinstance(responce, list):
                result = responce
            else:
                result = responce.get('detail')

            return result

    except Exception:
        logger.exception('Ошибка при получении чатов')
        
        return "Ошибка при получении чатов. Попробуйте позже."


async def request_to_finally(chat_id: int, user_question: str, date_send: str) -> str | dict:
    settings = get_bot_settings()
    
    URL = f'{settings.BACKEND_URL}/api/message/answer-to-user/'
    data = {
        'question': user_question,
        'timestamp': date_send,
        'chat_id': chat_id
    }
    
    logger.info('Отправили запрос на получение ответа от архивариуса...')

    try:
        async with request.session.post(URL, json=data) as responce:
            responce = await responce.json()
            result: str | None = responce.get('response').get('message')
            
            if result is None:
                result = responce.get('detail')

            return result

    except Exception:
        logger.exception('Ошибка при получении финального ответа')
        
        return "Ошибка при получении финального ответа. Попробуйте позже."