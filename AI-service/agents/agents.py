import datetime
from typing import TypeVar

from agents.agent import Agent
from agents.error import ai_retries
from constants.prompts import (
    FILTER_PROMPT,
    FINALLY_ANSWER_PROMPT,
    MESSAGE_VALIDATOR_PROMPT,
    QUESTION_VALIDATOR_PROMPT,
)
from schemas.response.model import (
    FilterOutput,
    FinallyAnswerOutput,
    MessageValidatorOutput,
    SafetyOutput,
    SimpleResponse,
)
from utils.config.config import get_app_settings
from utils.models.utils import date_injection

T = TypeVar(
    "T",
    SafetyOutput,
    MessageValidatorOutput,
    FilterOutput,
    FinallyAnswerOutput,
)
settings = get_app_settings()

agent_question_validator = Agent(model_name=settings.MODEL,
            system_prompt=QUESTION_VALIDATOR_PROMPT,
            pydantic_object=SafetyOutput
                  )

agent_chat_validator = Agent(model_name=settings.MODEL,
                  system_prompt=MESSAGE_VALIDATOR_PROMPT,
                  pydantic_object=MessageValidatorOutput
                  )

agent_filter_maker = Agent(model_name=settings.MODEL,
                  system_prompt=FILTER_PROMPT,
                  pydantic_object=FilterOutput
                  )


agent_replyer  = Agent(model_name=settings.MODEL,
                      system_prompt=FINALLY_ANSWER_PROMPT,
                      pydantic_object=FinallyAnswerOutput,
                      temperature=0.1
                      )

agent_checker = Agent(model_name=settings.MODEL,
        system_prompt='',
        pydantic_object=SimpleResponse,
        temperature=0.1)


async def call_agent(agent: Agent, data: str, error_msg: str, max_retries: int = 1) -> T:
    query = {'input_data': data}
        
    response: T = await ai_retries(max_retries,
            agent=agent,
            error_msg=error_msg,
            data_for_agent=query)
            
    return response
    
    
async def agent_for_question_validate(question: str) -> SafetyOutput:
    """Агент для валидации вопроса пользователя в личных сообщениях

    Args:
        question (str): Вопрос пользователя

    Returns:
        SafetyOutput | str: Ответ модели или сообщение об ошибке
    """
    
    response: SafetyOutput = await call_agent(
        agent=agent_question_validator,
        data=question,
        error_msg='Ошибка при валидации вопроса. Попробуйте еще раз'
    )
        
    return response


async def agent_for_chat_validate(message: str, send_day: datetime.datetime) -> MessageValidatorOutput:
    """Агент для валидации сообщение из чата
    
    Args:
        message (str): Текст сообщения
        send_day (datetime.datetime): День отправки
    
    Returns:
        MessageValidatorOutput | str: Ответ модели или сообщение об ошибке
    """
    
    date_part: str = await date_injection(date=send_day)
    
    finally_message = f"""
Контекст: {date_part}

Сообщение: {message}
    """
    
    response: MessageValidatorOutput = await call_agent(
            agent=agent_chat_validator,
            data=finally_message,
            error_msg='Ошибка при валидации сообщения. Попробуйте еще раз'
        )
            
    return response


async def agent_for_making_filter(question: str, date_send: datetime.datetime) -> FilterOutput:
    """Агент для создания фильтров поиска в БД
        
    Args:
        question (str): Вопрос пользователя
        date_send (datetime.datetime): День отправки
        
    Returns:
        FilterOutput | str: Ответ модели или сообщение об ошибке
    """
    
    date_part: str = await date_injection(date=date_send)
        
    finally_message = f"""
    Контекст: {date_part}
    
    Сообщение: {question}
    """

    response: FilterOutput = await call_agent(
                agent=agent_filter_maker,
                data=finally_message,
                error_msg='Ошибка при формировании фильтров. Попробуйте еще раз'
            )
    
    return response


async def agent_for_finally_response(message: str) -> FinallyAnswerOutput:
    """Агент для ответа на вопрос пользователя с домашним заданием

    Args:
        message (str): Сформированное сообщение в формате "сообщение - время"

    Returns:
        FinallyAnswerOutput | str: Ответ модели или сообщение об ошибке
    """
    
    response: FinallyAnswerOutput = await call_agent(
                agent=agent_replyer,
                data=message,
                error_msg='Ошибка при финальном ответе. Попробуйте еще раз'
            )
        
    return response


# Сделать двойную проверку чата (сначала факты, а уже потом ответ)