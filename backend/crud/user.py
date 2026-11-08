from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserChat


async def create_user(max_id: int, session: AsyncSession) -> int | None:
    """Функция, которая регистрирует пользователя

    Args:
        max_id (int): Max ID пользователя
        
        session (AsyncSession): Асинхронная сессия
    """
    
    stmt = (
        pg_insert(User)
        .values(max_id=max_id)
        .on_conflict_do_nothing(index_elements=["max_id"])
        .returning(User.user_id)
        )
    
    result = await session.execute(stmt)
    user_id = result.scalar()
    
    if user_id is None:
        response = await _get_user(User.max_id == max_id, session=session)
        user_id: int = response.scalar_one()
    
    return user_id


async def _get_user(*params, session: AsyncSession, fields: tuple = (User.user_id, )) -> Result[tuple[User]]:
    """Функция, которая возврашает объект/ы таблицы пользователя

    Args:
        session (AsyncSession): Асинхронная сессия
        fields (tuple, optional): Поля, которые мы хотим получить. По умолчанию (User.user_id, )

    Returns:
        Result[tuple[User]]: Результат запроса
    """
    
    query = select(*fields).where(*params)
    
    result = await session.execute(query)
    
    return result


async def create_user_chat(user_id: int, chat_id: int, session: AsyncSession) -> int:
    """Функция, которая создает объект чата пользователя и возвращает его ID

    Args:
        user_id (int): ID пользователя
        chat_id (int): Chat ID пользователя
        session (AsyncSession): Асинхронная сессия

    Returns:
        int: ID объекта
    """
    
    stmt = (
        pg_insert(UserChat)
        .values(user_id=user_id, chat_id=chat_id)
        .on_conflict_do_nothing(index_elements=["user_id", "chat_id"])
        .returning(UserChat.user_chat_id)
        )
        
    result = await session.execute(stmt)
    user_chat_id = result.scalar()
        
    if user_chat_id is None:
        response = await _get_user_chat(UserChat.user_id == user_id, UserChat.chat_id == chat_id, session=session)
        user_chat_id: int = response.scalar_one()
        
    return user_chat_id


async def _get_user_chat(*params, session: AsyncSession, fields: tuple = (UserChat.user_chat_id, )) -> Result[tuple[UserChat]]:
    """Функция, которая возврашает объект/ы таблицы чата пользователя

    Args:
        session (AsyncSession): Асинхронная сессия
        fields (tuple, optional): Поля, которые мы хотим получить. По умолчанию (UserChat.user_chat_id, )

    Returns:
        Result[tuple[UserChat]]: Результат запроса
    """
    
    query = select(*fields).where(*params)
    
    result = await session.execute(query)
    
    return result
    

async def add_chat_members(members_id: list[int], chat_id: int, session: AsyncSession):
    insert_users_stmt = (
        pg_insert(User)
        .values([{'max_id': mid} for mid in members_id])
        .on_conflict_do_nothing(index_elements=['max_id'])
    )
    
    await session.execute(insert_users_stmt)

    users_stmt = select(User.user_id).where(User.max_id.in_(members_id))
    result = await session.execute(users_stmt)
    user_ids = result.scalars().all()

    if user_ids:
        insert_user_chats_stmt = (
            pg_insert(UserChat)
            .values([{'user_id': uid, 'chat_id': chat_id} for uid in user_ids])
            .on_conflict_do_nothing(index_elements=['user_id', 'chat_id'])
        )
        
    await session.execute(insert_user_chats_stmt)