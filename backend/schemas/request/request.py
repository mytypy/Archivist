import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    chat_id: int = Field(description='Max ID чата')
    chat_title: str = Field(description='Название чата')
    max_id: int = Field(description='Max ID владельца сообщения')
    text: str = Field(description='Текст сообщения', min_length=6, max_length=256)
    timestamp: datetime.datetime = Field(description='Время отправки сообщения')


class UserQuestion(BaseModel):
    question: str = Field(description='Вопрос пользователя', min_length=6, max_length=64)
    timestamp: datetime.datetime = Field(description='Время отправки сообщения')
    chat_id: int = Field(description='Нужный чат пользователя')


class UserModel(BaseModel):
    user_ids: list[int] = Field(description='ID пользователей для добавления')
    chat_id: int = Field(description='ID чата')
    chat_title: str = Field(description='Название чата')