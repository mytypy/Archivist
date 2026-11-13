import logging

from fastapi import APIRouter

from agents.agents import (
    agent_for_chat_validate,
    agent_for_finally_response,
    agent_for_making_filter,
    agent_for_question_validate,
)
from schemas.request.request import (
    ForAnswerModel,
    ForFilterModel,
    MessageModel,
    QuestionModel,
)
from schemas.response.model import (
    FilterOutput,
    FinallyAnswerOutput,
    MessageValidatorOutput,
    SafetyOutput,
)
from utils.models.utils import normalize_data_to_message_for_reply

logger = logging.getLogger(name=__name__)
router = APIRouter(prefix='/model', tags=['Работа с агентами'])


@router.post('/validate-question/')
async def validate_question(data: QuestionModel) -> dict[str, SafetyOutput]:
    """Ручка для валидации запроса в личные сообщении бота

    Args:
        data (QuestionModel): Объект QuestionModel

    Returns:
        dict[str, SafetyOutput]: Результат с успешным ответом модели
    """
    
    my_response: SafetyOutput = await agent_for_question_validate(question=data.question)
        
    return {'response': my_response}


@router.post('/validate-chat-message/')
async def validate_chat_message(data: MessageModel) -> dict[str, MessageValidatorOutput]:
    """Ручка для валидации сообщения из чата

    Args:
        data (MessageModel): Объект MessageModel

    Returns:
        dict[str, MessageValidatorOutput]: Результат с успешным ответом модели
    """
    
    my_response: MessageValidatorOutput = await agent_for_chat_validate(message=data.message, send_day=data.date_send)
    
    return {'response': my_response}


@router.post('/get-filters/')
async def get_filters_from_model(data: ForFilterModel) -> dict[str, FilterOutput]:
    """Ручка для получения фильтров поиска в БД

    Args:
        data (ForFilterModel): Объект ForFilterModel

    Returns:
        dict[str, FilterOutput]: Результат с успешным ответом модели
    """
    
    my_response: FilterOutput = await agent_for_making_filter(question=data.question, date_send=data.date_send)
    
    return {'response': my_response}


@router.post('/get-answer/')
async def get_answer(data: ForAnswerModel) -> dict[str, FinallyAnswerOutput]:
    """Ручка для получения финального ответа с домашним заданием

    Args:
        data (ForAnswerModel): Объект ForAnswerModel

    Returns:
        dict[str, FinallyAnswerOutput]: Результат с успешным ответом модели
    """
    
    generate_message_for_agent: str = await normalize_data_to_message_for_reply(
        user_question=data.user_question,
        date_send=data.date_send,
        chat_history=data.chat_messages,
        date_range_start=data.date_range_start,
        date_range_stop=data.date_range_end
        )

    logger.info(generate_message_for_agent)
    
    my_response: FinallyAnswerOutput = await agent_for_finally_response(message=generate_message_for_agent)
            
    return {'response': my_response}


# Добавить мидлварь при проде и ничего, при дебаге