import datetime

from pydantic import BaseModel, Field


class SafetyOutput(BaseModel):
    reason: str = Field(description="Причина отказа ответа на вопрос для пользователя. Пусто, если is_safe=true", default_factory=str)
    is_safe: bool = Field(description="Безопасен ли запрос и относится ли он к ДЗ?", default_factory=bool)


class MessageValidatorOutput(BaseModel):
    is_homework: bool = Field(description='true, если сообщение относится к теме домашней работы', default_factory=bool)
    subject: str | None = Field(description='Название предмета, к которому относится сообщение. None, если его нет', default_factory=str)
    due_date: datetime.datetime | None = Field(description='Дата, на которую назначено домашнее задание. None, если дата не известна',
                                                default=None)