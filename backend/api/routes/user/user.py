import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from api.dependencies.auth.auth import is_bot
from crud.chat import create_chat, get_chats
from crud.user import add_chat_members, get_user, get_user_chats_db
from db.manager import get_db_session
from schemas.request.request import UserModel

router = APIRouter(prefix='/user', tags=['Обработка пользователя'])
bot_validator = Depends(is_bot)
session = Depends(get_db_session)
logger = logging.getLogger(name=__name__)


@router.post('/set-user/')
async def handle_message(message: UserModel, session: AsyncSession = session) -> JSONResponse:
    async with session.begin():
        chat_id = await create_chat(max_chat_id=message.chat_id, title=message.chat_title, session=session)
        await add_chat_members(members_id=message.user_ids, chat_id=chat_id, session=session)
    
    return JSONResponse(content={
        'response': 'Все ок!'
    })


@router.get('/get-user-chats/{max_user_id}')
async def get_user_chats(max_user_id: int, session: AsyncSession = session):
    user_id = await get_user(max_id=max_user_id, session=session)
    
    if user_id is None:
        raise HTTPException(detail='Вас еще нет ни в одном чате. Добавьте меня в свой чат', status_code=status.HTTP_404_NOT_FOUND)

    user_chats: list[int] = await get_user_chats_db(user_id=user_id, session=session)
    user_chats_with_title = await get_chats(chats_id=user_chats, session=session)
    
    return user_chats_with_title