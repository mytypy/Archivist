from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Model, int_pk


class Chat(Model):
    __tablename__ = 'chat'
    
    chat_id: Mapped[int_pk]
    max_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)