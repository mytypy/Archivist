import datetime

from agents.agent import Agent
from agents.error import ai_retryies
from constants.prompts import (
    FILTER_PROMPT,
    FINALLY_ANSWER_PROMPT,
    MESSAGE_VALIDATOR_PROMPT,
    QUESTION_VALIDATOR_PROMPT,
)
from constants.settings import MODEL
from schemas.model.model import (
    FilterOutput,
    FinallyAnswerOutput,
    MessageValidatorOutput,
    SafetyOutput,
)
from utils.utils import date_injection


async def agent_validator(question: str) -> SafetyOutput | str:
    """Агент, который валидирует вопрос пользователя в личных сообщениях

    Args:
        question (str): Вопрос пользователя

    Returns:
        SafetyOutput | str: Ответ модели или сообщение об ошибке
    """
    
    agent = Agent(model_name=MODEL,
                  system_prompt=QUESTION_VALIDATOR_PROMPT,
                  pydantic_object=SafetyOutput
                  )
    
    query = {'input_data': question}
    
    response: str | SafetyOutput = await ai_retryies(max_retries=1, agent=agent,
                           error_msg='Ошибка при валидации вопроса. Попробуйте еще раз',
                           data_for_agent=query)
        
    return response


async def agent_chat_validator(message: str, send_day: datetime.datetime) -> MessageValidatorOutput | str:
    """Агент, который валидирует сообщение из чата
    
    Args:
        message (str): Текст сообщения
        send_day (datetime.datetime): День отправки
    
    Returns:
        MessageValidatorOutput | str: Ответ модели или сообщение об ошибке
    """
        
    agent = Agent(model_name=MODEL,
                  system_prompt=MESSAGE_VALIDATOR_PROMPT,
                  pydantic_object=MessageValidatorOutput
                  )
    
    date_part: str = await date_injection(date=send_day)
    
    finally_message = f"""
Контекст: {date_part}

Сообщение: {message}
    """
        
    query = {'input_data': finally_message}
    
    response: str | MessageValidatorOutput = await ai_retryies(max_retries=1, agent=agent,
                           error_msg='Ошибка при валидации сообщения. Попробуйте еще раз',
                           data_for_agent=query)
        
    return response


async def agent_filter_maker(question: str, date_send: datetime.datetime) -> str | FilterOutput:
    """Агент, который выдает фильтры для поиска в БД
        
    Args:
        question (str): Вопрос пользователя
        date_send (datetime.datetime): День отправки
        
    Returns:
        FilterOutput | str: Ответ модели или сообщение об ошибке
    """
    
    agent = Agent(model_name=MODEL,
                  system_prompt=FILTER_PROMPT,
                  pydantic_object=FilterOutput
                  )
    
    date_part: str = await date_injection(date=date_send)
        
    finally_message = f"""
    Контекст: {date_part}
    
    Сообщение: {question}
    """
    
    query = {'input_data': finally_message}
    
    response: str | FilterOutput = await ai_retryies(max_retries=1, agent=agent,
                            error_msg='Ошибка при формировании фильтров. Попробуйте еще раз',
                            data_for_agent=query)
    
    return response


async def agent_replyer(message: str) -> FinallyAnswerOutput | str:
    """Агент, который выдает ответ на вопрос пользователя с домашним заданием

    Args:
        message (str): Сформированное сообщение в формате "сообщение - время"

    Returns:
        FinallyAnswerOutput | str: Ответ модели или сообщение об ошибке
    """
    agent = Agent(model_name=MODEL,
                      system_prompt=FINALLY_ANSWER_PROMPT,
                      pydantic_object=FinallyAnswerOutput,
                      temperature=0.1
                      )
        
    query = {'input_data': message}
        
    response: str | FinallyAnswerOutput = await ai_retryies(max_retries=1, agent=agent,
                    error_msg='Ошибка при финальном ответе. Попробуйте еще раз',
                    data_for_agent=query)
        
    return response


# Сделать двойную проверку чата (сначала факты, а уже потом ответ)