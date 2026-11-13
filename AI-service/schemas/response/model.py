import datetime

from pydantic import BaseModel, Field


class SafetyOutput(BaseModel):
    """Модель для валидации ответа при проверке запроса в ЛС"""
    
    reason: str = Field(description="Причина отказа ответа на вопрос для пользователя. Пусто, если is_safe=true", default_factory=str)
    is_safe: bool = Field(description="Безопасен ли запрос и относится ли он к ДЗ?", default_factory=bool)


class MessageValidatorOutput(BaseModel):
    """Модель для валидации ДЗ из чата"""
    
    is_homework: bool = Field(description='true, если сообщение относится к теме домашней работы', default_factory=bool)
    subject: str | None = Field(description='Название предмета, к которому относится сообщение. None, если его нет', default=None)
    due_date: datetime.datetime | None = Field(description='Дата, на которую назначено домашнее задание. None, если дата не известна',
                                                default=None)


class FilterOutput(BaseModel):
    """Модель для валидации фильтров"""
    
    subject: str | None = Field(description='Название предмета, к которому относится сообщение. None, если его нет', default=None)
    target_date: datetime.datetime | None = Field(description='Целевая дата, на которую нужно найти домашнее задание. None, если дата не известна',
                                                    default=None)


class FinallyAnswerOutput(BaseModel):
    """Модель для валидации финального ответа для пользователя"""
    
    message: str = Field(description='Ответ с домашним заданием для пользователя')


class SimpleResponse(BaseModel):
    """Модель для обычного ответа при прогреве модели"""
    
    message: str = Field(description='Просто ответ')