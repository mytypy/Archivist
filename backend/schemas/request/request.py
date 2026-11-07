import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    chat_id: int = Field(description='Max ID чата')
    max_id: int = Field(description='Max ID владельца сообщения')
    text: str = Field(description='Текст сообщения', max_length=564)
    timestamp: datetime.datetime = Field(description='Время отправки сообщения')


class UserQuestion(BaseModel):
    question: str = Field(description='Вопрос пользователя', min_length=6, max_length=64)
    timestamp: datetime.datetime = Field(description='Время отправки сообщения')
    chat_id: int = Field(description='Нужный чат пользователя')