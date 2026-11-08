import datetime

from pydantic import BaseModel, Field


class QuestionModel(BaseModel):
    """Модель для валидации вопроса боту"""
    
    question: str = Field(min_length=6, max_length=64, description='Вопрос пользователя боту')


class MessageModel(BaseModel):
    """Модель для валидации сообщения из чата"""
    
    message: str = Field(min_length=6, max_length=256, description='Сообщение из чата')
    date_send: datetime.datetime = Field(description='Дата отправки сообщения в чате')


class ForFilterModel(BaseModel):
    """Модель для валидации сообщения из чата для фильтра"""
    
    question: str = Field(min_length=6, max_length=64, description='Вопрос боту')
    date_send: datetime.datetime = Field(description='Дата отправки сообщения боту')
    
    
class ChatMessageModel(BaseModel):
    """Модель для валидации объекта сообщения из чата"""
    
    message: str = Field(description='Сообщение из чата')
    date_send: datetime.datetime = Field(description='Дата отправки сообщения')
    
    
class ForAnswerModel(BaseModel):
    """Модель для валидации финального запроса"""
    
    user_question: str = Field(min_length=6, max_length=64, description='Вопрос пользователя')
    date_send: datetime.datetime = Field(description='Время отправки сообщения')
    
    chat_messages: list[ChatMessageModel] = Field(description='Сообщения из чата')
    
    date_range_start: datetime.datetime = Field(description='Начало промежутка поиска')
    date_range_end: datetime.datetime = Field(description='Конец промежутка поиска')