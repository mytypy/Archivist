import datetime

from constants.other import DAYS_RU
from schemas.request.request import ChatMessageModel


async def date_injection(date: datetime.datetime) -> str:
    """Функция для нормализации даты в строку в готовом формате 

    Args:
        date (datetime.datetime): Объект даты

    Returns:
        str: строка в формате 'Сегодня [Число] [День недели], [ГГГГ-ММ-ДД ЧЧ-ММ-СС]'
    """
    week_day = DAYS_RU[date.weekday()]
    format_day = date.strftime("%Y-%m-%d %H:%M:%S")
        
    date_message = f"Сегодня {date.day} {week_day}, {format_day}"
    
    return date_message


async def normalize_data_to_message_for_reply(user_question: str, date_send: datetime.datetime,
                                              chat_history: list[ChatMessageModel],
                                              date_range_start: datetime.datetime,
                                              date_range_stop: datetime.datetime
                                              ) -> str: 
    """Функция для формирования текста c сообщениями из чата
    
    Args:
        user_question (str): Вопрос пользователя
        chat_history (list[ChatMessageModel]): Список с объектами ChatMessageModel
        date_range_start (datetime.datetime): Начало промежутка сообщений
        date_range_stop (datetime.datetime): Конец промежутка сообщений
    
    Returns:
        str: Текст для агента
    """
    
    normalize_date: str = await date_injection(date=date_send)
    history_during = f'{date_range_start.strftime("%Y-%m-%d %H:%M:%S")} - {date_range_stop.strftime("%Y-%m-%d %H:%M:%S")}'
    
    message_to_model = f"""
Дата: {normalize_date}
Вопрос: {user_question}
История чата за {history_during}:"""
    
    for message in chat_history:
        formated_date = message.date_send.strftime("%Y-%m-%d %H:%M:%S")
        formated_message = f'\n   - {message.message} - [{formated_date}]'
        
        message_to_model += formated_message
    
    return message_to_model