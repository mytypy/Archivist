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
    request_to_validate_chat_message,
    request_to_validate_user_question,
    request_to_get_filters
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
    # validation_result: str | dict = await request_to_validate_chat_message(message=message.text, date_send=message.timestamp)

    # if isinstance(validation_result, str) is True:
    #     raise HTTPException(detail=validation_result, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # is_homework: bool = validation_result['is_homework']

    # if is_homework is False:
    #     raise HTTPException(detail='Данное сообщение не является ДЗ', status_code=status.HTTP_400_BAD_REQUEST)

    # subject: str | None = validation_result['subject']
    # due_date: datetime.datetime | None = validation_result['due_date']

    subject: str | None = None
    due_date: datetime.datetime | None = None
    
    max_id: int = message.max_id
    max_chat_id: int = message.chat_id
    
    user_id = await get_user_cache(max_id=max_id)
    chat_id = await get_chat_cache(chat_max_id=max_chat_id)
    user_chat_id = await get_user_chat(max_id=max_id, chat_max_id=max_chat_id)
    
    async with session.begin(): # Тут авто-коммит
        if not user_id:
            user_id = await create_user(max_id=max_id, session=session)
            await set_user_cache(max_id=max_id, user_id=user_id)
        
        if not chat_id:
            chat_id = await create_chat(max_chat_id=max_chat_id, session=session)
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
async def answer_to_user(data: UserQuestion, session: AsyncSession = session):
    result: str | dict = await request_to_validate_user_question(question=data.question)

    if isinstance(result, str) is True:
        raise HTTPException(detail=result, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    is_safe: bool = result['is_safe']
    reason: str = result['reason']

    if is_safe is False:
        reason = reason if reason else "Я не отвечаю на такие вопросы, извините."
        raise HTTPException(detail=reason, status_code=status.HTTP_400_BAD_REQUEST)

    filters_response = await request_to_get_filters(message=data.question,
                                                    date_send=data.timestamp)

    subject: str | None = filters_response['subject']
    due_date: str = filters_response['target_date']
    due_date_in_dt: datetime.datetime = datetime.datetime.fromisoformat(due_date)

    await get_messages_with_filter(subject=subject, target_date=due_date_in_dt, chat_id=data.chat_id, session=session)
    
    
# Добавление людей из чата в БД