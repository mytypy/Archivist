import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio.session import AsyncSession

from api.dependencies.auth.auth import is_bot
from crud.chat import create_chat
from crud.user import add_chat_members
from db.manager import get_db_session
from schemas.request.request import UserModel

router = APIRouter(prefix='/user', tags=['Обработка сообщений'])
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