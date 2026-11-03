import datetime

from pydantic import BaseModel, Field


class QuestionModel(BaseModel):
    question: str = Field(min_length=6, max_length=64, description='Вопрос пользователя боту')


class MessageModel(BaseModel):
    message: str = Field(min_length=6, max_length=256, description='Сообщение из чата')
    date_send: datetime.datetime = Field(description='Дата отправки сообщения')


class ForAnswerModel(BaseModel):
    text_for_llm: str = Field(description='Итоговые данные из БД для модели')