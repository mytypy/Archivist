from fastapi import APIRouter, Response

from agents.agents import agent_chat_validator, agent_validator
from schemas.request.request import ForAnswerModel, MessageModel, QuestionModel

router = APIRouter(prefix='/model', tags=['Работа с агентами'])


@router.post('/validate-question')
async def validate_question(data: QuestionModel, response: Response):
    my_response = await agent_validator(question=data.question)
    
    response.status_code = 500 if isinstance(my_response, str) is False else 200
    
    return {'response': my_response}


@router.post('/validate-chat-message')
async def validate_chat_message(data: MessageModel, response: Response):
    my_response = await agent_chat_validator(message=data.message, send_day=data.date_send)
        
    response.status_code = 500 if isinstance(my_response, str) is False else 200
        
    return {'response': my_response}


@router.post('/get-filters')
async def get_filters_from_model(data: QuestionModel):
    ...


@router.post('/get-answer')
async def get_answer(data: ForAnswerModel):
    ...


# Добавить мидлварь при проде и ничего, при дебаге