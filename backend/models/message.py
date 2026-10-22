from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Model, created_at_time, int_pk


class Message(Model):
    __tablename__ = 'message'
    
    message_id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='SET NULL'), nullable=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chat.chat_id', ondelete='CASCADE'))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[created_at_time]