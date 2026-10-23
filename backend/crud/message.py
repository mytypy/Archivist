import datetime

from sqlalchemy import Result, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.utils import db_errors_to_http
from models.message import Message


async def create_message(user_id: int, chat_id: int, text: str, timestamp: datetime.datetime, session: AsyncSession) -> None:
    """Функция, которая создает объект сообщения в БД

    Args:
        user_id (int): ID пользователя
        chat_id (int): ID чата
        text (str): Текст сообщения
        timestamp (datetime.datetime): Вреям отправки сообщения
        session (AsyncSession): Асинхронная сессия
    """
    
    stmt = insert(Message).values(
        user_id=user_id,
        chat_id=chat_id,
        text=text,
        created_at=timestamp
    )
    
    await session.execute(stmt)


async def get_message(*params, session: AsyncSession, fields: tuple = (Message.message_id, )) -> Result[tuple[Message]]:
    """Функция, которая возврашает объект/ы сообщения

    Args:
        session (AsyncSession): Асинхронная сессия
        fields (tuple, optional): Поля, которые мы хотим получить. По умолчанию (Message.message_id, )

    Returns:
        Result[tuple[Message]]: Результат запроса
    """
    
    query = select(*fields).where(*params)
    
    result = await session.execute(query)
    
    return result