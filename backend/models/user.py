from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Model, int_pk


class User(Model):
    __tablename__ = 'user'
    
    user_id: Mapped[int_pk]
    max_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)


class UserChat(Model):
    __tablename__ = 'user_chats'
    
    user_chat_id: Mapped[int_pk]
    
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'))
    chat_id: Mapped[int] = mapped_column(ForeignKey('chat.chat_id', ondelete='CASCADE'))
