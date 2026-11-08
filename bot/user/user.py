import datetime
import logging

from maxapi import F, Router
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types import MessageCallback, MessageCreated

from constants.messages import START_MESSAGE
from keyboard.keyboard import ask_question_buttons, chats_button, go_back
from services.requests.request import get_user_chats_from_db, request_to_finally

logger = logging.getLogger(name=__name__)
router = Router('user_router')


class AskHomework(StatesGroup):
    enter_question = State()
    
    
@router.message_created(F.message.body.text == 'Узнать ДЗ', F.chat.type == 'dialog')
async def get_user_chats(event: MessageCreated):
    user_id: int = event.from_user.user_id
    
    user_chats = await get_user_chats_from_db(max_user_id=user_id)
    
    if isinstance(user_chats, str):
        await event.message.answer(
            text=user_chats
        )
    elif user_chats:
        await event.message.answer(
            text='Вот ваши чаты (пока что отображаем максимум 3, так как пагинация в процессе разработки)',
            attachments=[
                await chats_button(data=user_chats)
                ]
        )


@router.message_callback(F.callback.payload.isdigit())
async def handle_callback(callback: MessageCallback, context: MemoryContext):
    chat_id = callback.message.recipient.chat_id
    payload = callback.callback.payload
    
    await callback.delete()
    
    await context.update_data(chat_id=int(payload))
    await context.set_state(AskHomework.enter_question)
    
    await callback.bot.send_message(
        chat_id=chat_id,
        text='Какой вопрос вас интересует?',
        attachments=[
            await go_back()
        ]
    )


@router.message_callback(F.callback.payload == 'Главное меню')
async def handle_callback_menu(callback: MessageCallback, context: MemoryContext):
    await context.clear()
    chat_id = callback.message.recipient.chat_id
        
    await callback.bot.send_message(
        chat_id=chat_id,
        text=START_MESSAGE,
        attachments=[
            await ask_question_buttons()
        ]
    )

@router.message_created(F.message.body.text == 'Главное меню', F.chat.type == 'dialog')
async def go_back_menu(event: MessageCreated, context: MemoryContext):
    await context.clear()
    
    await event.message.answer(
        text=START_MESSAGE,
        attachments=[
            await ask_question_buttons()
        ]
    )
    

@router.message_created(AskHomework.enter_question)
async def get_question(event: MessageCreated, context: MemoryContext):
    
    data = await context.get_data()
    
    chat_id: int = data.get("chat_id")
    question: str = event.message.body.text
    
    if not (6 <= len(question) <= 64):
        await event.message.answer("Сообщение должно быть больше 6 и меньше 64 символов!")
        await event.message.answer(
                text='Какой вопрос вас интересует?',
                attachments=[
                    await go_back()
                ]
            )
        await context.set_state(AskHomework.enter_question)
        
        return
        
    date_send: datetime.datetime = datetime.datetime.fromtimestamp(event.timestamp / 1000)
        
    formated_date_send: str = date_send.strftime("%Y-%m-%d %H:%M:%S")
    
    await context.clear()
    await event.message.answer(f"Ищу ДЗ по чату. Вопрос: {question}")
    
    result = await request_to_finally(chat_id=chat_id, user_question=question, date_send=formated_date_send)
    
    await event.message.answer(
        text=result,
        attachments=[
            await ask_question_buttons()
        ]
    )