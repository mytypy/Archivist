import datetime

from sqlalchemy import Result, insert, select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message


async def create_message(user_id: int, chat_id: int,
                        text: str, timestamp: datetime.datetime,
                        subject: str | None, due_date: datetime.datetime | None,
                            session: AsyncSession) -> None:
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
        created_at=timestamp,
        subject=subject,
        due_date=due_date
    )
    
    await session.execute(stmt)


async def _get_message(*params, session: AsyncSession, fields: tuple = (Message.message_id, )) -> Result[tuple[Message]]:
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


async def get_messages_with_filter(subject: str | None, target_date: datetime.datetime,
                                   chat_id: int,
                                    session: AsyncSession) -> list[dict]:
    seven_days_ago = target_date - datetime.timedelta(days=7)

    
    stmt = (
        select(Message.text, Message.created_at)
        .where(
            Message.chat_id == chat_id,
            (Message.due_date == target_date) | (
                (Message.subject == subject) & 
                (Message.created_at <= target_date) & 
                (Message.created_at >= seven_days_ago)
            )
            )
        .order_by(asc(Message.created_at))
        .limit(15)
    )

    result = await session.execute(stmt)

    print(result.mappings().all())
