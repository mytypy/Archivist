from fastapi import APIRouter, Response

from agents.agents import (
    agent_chat_validator,
    agent_filter_maker,
    agent_replyer,
    agent_validator,
)
from schemas.model.model import (
    FilterOutput,
    FinallyAnswerOutput,
    MessageValidatorOutput,
    SafetyOutput,
)
from schemas.request.request import (
    ForAnswerModel,
    ForFilterModel,
    MessageModel,
    QuestionModel,
)
from utils.utils import normalize_data_to_message_for_reply

router = APIRouter(prefix='/model', tags=['Работа с агентами'])


@router.post('/validate-question/')
async def validate_question(data: QuestionModel, response: Response) -> dict[str, SafetyOutput | str]:
    """Ручка для валидации запроса в личные сообщении бота

    Args:
        data (QuestionModel): Объект QuestionModel
        response (Response): Объект ответа

    Returns:
        dict[str, SafetyOutput | str]: Ответ с строкой ошибки или с успешным ответом модели
    """
    
    my_response = await agent_validator(question=data.question)
    
    response.status_code = 500 if isinstance(my_response, str) is True else 200
    
    return {'response': my_response}


@router.post('/validate-chat-message/')
async def validate_chat_message(data: MessageModel, response: Response) -> dict[str, MessageValidatorOutput | str]:
    """Ручка для валидации сообщения из чата

    Args:
        data (MessageModel): Объект MessageModel
        response (Response): Объект ответа

    Returns:
        dict[str, MessageValidatorOutput | str]: Ответ с строкой ошибки или с успешным ответом модели
    """
    
    my_response = await agent_chat_validator(message=data.message, send_day=data.date_send)
        
    response.status_code = 500 if isinstance(my_response, str) is True else 200
        
    return {'response': my_response}


@router.post('/get-filters/')
async def get_filters_from_model(data: ForFilterModel, response: Response) -> dict[str, FilterOutput | str]:
    """Ручка для получения фильтров поиска в БД

    Args:
        data (ForFilterModel): Объект ForFilterModel
        response (Response): Объект ответа

    Returns:
        dict[str, FilterOutput | str]: Ответ с строкой ошибки или с успешным ответом модели
    """
    
    my_response = await agent_filter_maker(question=data.message, date_send=data.date_send)
    
    response.status_code = 500 if isinstance(my_response, str) is True else 200
            
    return {'response': my_response}


@router.post('/get-answer/')
async def get_answer(data: ForAnswerModel, response: Response) -> dict[str, FinallyAnswerOutput | str]:
    """Ручка для получения финального ответа с домашним заданием

    Args:
        data (ForAnswerModel): Объект ForAnswerModel
        response (Response): Объект ответа

    Returns:
        dict[str, FinallyAnswerOutput | str]: Ответ с строкой ошибки или с успешным ответом модели
    """
    
    generate_message_for_agent: str = await normalize_data_to_message_for_reply(
        user_question=data.user_question,
        date_send=data.date_send,
        chat_history=data.chat_messages,
        date_range_start=data.date_range_start,
        date_range_stop=data.date_range_end
        )

    print(generate_message_for_agent)
    my_response = await agent_replyer(message=generate_message_for_agent)
        
    response.status_code = 500 if isinstance(my_response, str) is True else 200
                
    return {'response': my_response}


# Добавить мидлварь при проде и ничего, при дебаге