import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from api.dependencies.auth.auth import is_bot
from crud.chat import create_chat
from crud.message import create_message
from crud.user import create_user, create_user_chat
from db.manager import get_db_session
from schemas.request.request import Message
from services.utils.auth.auth import (
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


@router.post('/add/')
async def handle_message(message: Message, session: AsyncSession = session) -> JSONResponse:
    max_id: int = message.max_id
    max_chat_id: int = message.chat_id
    
    user_id = int(await get_user_cache(max_id=max_id))
    chat_id = int(await get_chat_cache(chat_max_id=max_chat_id))
    user_chat_id = int(await get_user_chat(max_id=max_id, chat_max_id=max_chat_id))
    
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
                             text=message.text, timestamp=message.timestamp, session=session)
            
    return JSONResponse(content={'response': 'Сообщение успешно создано'}, status_code=status.HTTP_200_OK)