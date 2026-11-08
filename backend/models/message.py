import datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Model, int_pk


class Message(Model):
    __tablename__ = 'message'
    
    message_id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='SET NULL'), nullable=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chat.chat_id', ondelete='CASCADE'))
    reply_to: Mapped[int] = mapped_column(ForeignKey('message.message_id', ondelete='CASCADE'), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(String(64), nullable=True)
    
    due_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True) # Сухая дата
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False)) # Дата со временем