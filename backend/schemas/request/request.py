import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    chat_id: int = Field(description='Max ID чата')
    max_id: int = Field(description='Max ID владельца сообщения')
    text: str = Field(description='Текст сообщения', max_length=564)
    timestamp: datetime.datetime = Field(description='Время отправки сообщения')