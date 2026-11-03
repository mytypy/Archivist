import datetime

from agents.agent import Agent
from agents.error import ai_retryies

from constants.prompts import (
    MESSAGE_VALIDATOR_PROMPT,
    QUESTION_VALIDATOR_PROMPT
    )

from constants.settings import MODEL, URL
from constants.other import DAYS_RU
from schemas.model.model import SafetyOutput, MessageValidatorOutput


async def agent_validator(question: str) -> SafetyOutput | str:
    agent = Agent(model_name=MODEL,
                  system_prompt=QUESTION_VALIDATOR_PROMPT,
                  pydantic_object=SafetyOutput,
                  url=URL
                  )
    
    query = {'input_data': question}
    
    response: str | SafetyOutput = await ai_retryies(max_retries=1, agent=agent,
                           error_msg='Ошибка при валидации вопроса. Попробуйте еще раз',
                           data_for_agent=query)
        
    return response


async def agent_chat_validator(message: str, send_day: datetime.datetime) -> MessageValidatorOutput | str:
    agent = Agent(model_name=MODEL,
                  system_prompt=MESSAGE_VALIDATOR_PROMPT,
                  pydantic_object=MessageValidatorOutput,
                  url=URL
                  )
    
    week_day = DAYS_RU[send_day.weekday()]
    format_day = send_day.strftime("%Y-%m-%d %H:%M:%S")
    
    
    finally_message = f"""
Контекст: Сегодня {send_day.day} {week_day}, {format_day}

Сообщение: {message}
    """
    
    print(finally_message)
    
    query = {'input_data': finally_message}
    
    response: str | MessageValidatorOutput = await ai_retryies(max_retries=1, agent=agent,
                           error_msg='Ошибка при валидации сообщения. Попробуйте еще раз',
                           data_for_agent=query)
        
    return response



async def agent_filter_maker(query: str):
    ...


async def agent_replyer(query: str):
    ...