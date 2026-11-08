from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Model, int_pk


class Chat(Model):
    __tablename__ = 'chat'
    
    chat_id: Mapped[int_pk]
    title: Mapped[str] = mapped_column(String(33), nullable=False)
    max_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)