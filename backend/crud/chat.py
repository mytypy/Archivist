from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from db.utils import db_errors_to_http
from models.chat import Chat


async def create_chat(max_chat_id: int, session: AsyncSession) -> int | None:
    """Функция, которая регистрирует чат

    Args:
        max_chat_id (int): Max Chat ID чата
        
        session (AsyncSession): Асинхронная сессия
    """
    
    stmt = (
        pg_insert(Chat)
        .values(max_chat_id=max_chat_id)
        .on_conflict_do_nothing(index_elements=["max_chat_id"])
        .returning(Chat.chat_id)
        )
    
    result = await session.execute(stmt)
    chat_id = result.scalar()
    
    if chat_id is None:
        response = await get_chat(Chat.max_chat_id == max_chat_id, session=session)
        chat_id: int = response.scalar_one()
    
    return chat_id


async def get_chat(*params, session: AsyncSession, fields: tuple = (Chat.chat_id, )) -> Result[tuple[Chat]]:
    """Функция, которая возврашает объект/ы таблицы чата

    Args:
        session (AsyncSession): Асинхронная сессия
        fields (tuple, optional): Поля, которые мы хотим получить. По умолчанию (Chat.chat_id, )

    Returns:
        Result[tuple[Chat]]: Результат запроса
    """
    
    query = select(*fields).where(*params)
    
    result = await session.execute(query)
    
    return result