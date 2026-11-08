import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from api.dependencies.auth.auth import is_bot
from crud.chat import create_chat
from crud.message import create_message, get_messages_with_filter
from crud.user import create_user, create_user_chat
from db.manager import get_db_session
from schemas.request.request import Message, UserQuestion
from services.requests.request import (
    request_to_finally_request,
    request_to_get_filters,
    request_to_validate_chat_message,
    request_to_validate_user_question,
)
from utils.auth.auth import (
    get_chat_cache,
    get_user_cache,
    get_user_chat,
    set_chat_cache,
    set_user_cache,
    set_user_chat,
)

router = APIRouter(prefix='/message', tags=['Обработка сообщений'])
bot_validator = Depends(is_bot)
session = Depends(get_db_session)
logger = logging.getLogger(name=__name__)


@router.post('/add-message/')
async def handle_message(message: Message, session: AsyncSession = session) -> JSONResponse:
    """Эндпоинт для добавления сообщения из чата в БД

    Args:
        message (Message): Объект сообщения
        session (AsyncSession, optional): Асинхронная сессия

    Raises:
        HTTPException: Ошибка, если получили строку с ошибкой от llm сервиса
        HTTPException: Ошибка, если сообщение не относится к теме ДЗ

    Returns:
        JSONResponse: Сообщение об успешном добавлении сообщения в БД
    """
    
    validation_result: str | dict = await request_to_validate_chat_message(message=message.text, date_send=message.timestamp)

    if isinstance(validation_result, str) is True:
        raise HTTPException(detail=validation_result, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    is_homework: bool = validation_result['is_homework']

    if is_homework is False:
        raise HTTPException(detail='Данное сообщение не относится к теме ДЗ', status_code=status.HTTP_400_BAD_REQUEST)

    subject: str | None = validation_result['subject']
    due_date: datetime.date = datetime.datetime.fromisoformat(validation_result['due_date']).date() # Берем сухую дату (Год-месяц-день)
    
    max_id: int = message.max_id
    max_chat_id: int = message.chat_id
    chat_title: str = message.chat_title
    
    
    user_id = await get_user_cache(max_id=max_id)
    chat_id = await get_chat_cache(chat_max_id=max_chat_id)
    user_chat_id = await get_user_chat(max_id=max_id, chat_max_id=max_chat_id)
    
    async with session.begin(): # Тут авто-коммит
        if not user_id:
            user_id = await create_user(max_id=max_id, session=session)
            await set_user_cache(max_id=max_id, user_id=user_id)
        
        if not chat_id:
            chat_id = await create_chat(max_chat_id=max_chat_id, title=chat_title, session=session)
            await set_chat_cache(chat_max_id=max_chat_id, chat_id=chat_id)
        
        if not user_chat_id:
            user_chat_id = await create_user_chat(user_id=user_id, chat_id=chat_id, session=session)
            await set_user_chat(max_id=max_id, chat_max_id=max_chat_id, user_chat_id=user_chat_id)
        
        await create_message(user_id=user_id, chat_id=chat_id,
                             text=message.text,
                             due_date=due_date,
                             subject=subject,
                             timestamp=message.timestamp,
                               session=session)
            
    return JSONResponse(content={'response': 'Сообщение успешно создано'}, status_code=status.HTTP_200_OK)


@router.post("/answer-to-user/")
async def answer_to_user(data: UserQuestion, session: AsyncSession = session) -> JSONResponse:
    """Эндпоинт для обработки вопроса пользователя о ДЗ

    Args:
        data (UserQuestion): Объект вопроса
        response (Response): Объект ответа
        session (AsyncSession, optional): Асинхронная сессия

    Raises:
        HTTPException: Ошибка, если получили строку с ошибкой от llm сервиса при валидации
        HTTPException: Ошибка, если сообщение не относится к теме ДЗ
        HTTPException: Ошибка, если получили строку с ошибкой от llm сервиса при получении фильтров для поиска сообщений
        HTTPException: Ошибка, если получили строку с ошибой от llm сервиса при формировании финального ответа

    Returns:
        JSONResponse: Ответ модели
    """
    user_question: str = data.question
    question_date_send: datetime.datetime = data.timestamp
    str_user_question_date_send: str = question_date_send.strftime("%Y-%m-%d %H:%M:%S")
    
    validation_result: str | dict = await request_to_validate_user_question(question=user_question)
    
    if isinstance(validation_result, str) is True:
        raise HTTPException(detail=validation_result, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    is_safe: bool = validation_result['is_safe']
    reason: str = validation_result['reason']

    if is_safe is False:
        reason: str = reason if reason else "Я не отвечаю на такие вопросы, извините."
        raise HTTPException(detail=reason, status_code=status.HTTP_400_BAD_REQUEST)

    filters_response: str | dict = await request_to_get_filters(question=user_question,
                                                    date_send=str_user_question_date_send)
    
    if isinstance(filters_response, str) is True:
        raise HTTPException(detail=filters_response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    subject: str | None = filters_response['subject']
    message_target_date: str = filters_response['target_date']
    
    target_date_in_date_format: datetime.datetime = datetime.datetime.fromisoformat(message_target_date).replace(tzinfo=None) # Так как я поставил timezone=False на уровне БД
    target_date_in_seven_days_ago: datetime.datetime = (target_date_in_date_format - datetime.timedelta(days=7)).replace(tzinfo=None)
    
    messages: list[dict] = await get_messages_with_filter(subject=subject, target_date=target_date_in_date_format,
                                              days_ago=target_date_in_seven_days_ago,
                                              chat_id=data.chat_id, session=session)
    
    logger.info(messages)
    str_target_date: str = target_date_in_date_format.strftime("%Y-%m-%d %H:%M:%S")
    str_date_in_seven_days_ago: str = target_date_in_seven_days_ago.strftime("%Y-%m-%d %H:%M:%S")
    
    response_from_finally_agent = await request_to_finally_request(
        user_question=user_question,
        date_send=str_user_question_date_send,
        chat_messages=messages,
        date_range_start=str_date_in_seven_days_ago,
        date_range_end=str_target_date
    )
    
    if isinstance(response_from_finally_agent, str) is True:
        raise HTTPException(detail=response_from_finally_agent, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    return JSONResponse(content={
        'response': response_from_finally_agent
    }, status_code=status.HTTP_200_OK)

    
# Добавление людей из чата в БД