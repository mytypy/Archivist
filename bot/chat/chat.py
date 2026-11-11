import datetime
import logging

from maxapi import F, Router
from maxapi.types import BotAdded, BotAdminPermissionsChanged, MessageCreated

from constants.messages import START_CHAT_MESSAGE
from services.requests.request import request_to_add_users, send_message_to_server
from utils.chat.chat import get_ids_from_all_members

logger = logging.getLogger(name=__name__)
router = Router('chat_router')


@router.bot_added()
async def bot_added(event: BotAdded):
    chat_id: int = event.chat_id
    
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=START_CHAT_MESSAGE
    )
    
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Провожу инициализацию...'
    )
    
    members_id: list[int] | list = await get_ids_from_all_members(manager=event.chat.members)
    
    if not members_id:
        await event.bot.send_message(
            chat_id=event.chat_id,
            text='Не удалось получить всех участников из чата. Пожалуйста, добавьте меня в беседу еще раз или напишите в службу поддержки'
        )
    
    response_for_add_user: str | dict = await request_to_add_users(members_id=members_id, chat_id=chat_id, chat_title=event.chat.title[:32])
    
    if isinstance(response_for_add_user, str):
        logger.error(f'Ошибка при записи пользователей в БД: {response_for_add_user}. Chat_id: {chat_id}')
        
        await event.bot.send_message(
            chat_id=event.chat_id,
            text='Не удалось получить всех участников из чата. Пожалуйста, добавьте меня в беседу еще раз или напишите в службу поддержки'
        )
    else:
        message = response_for_add_user['response']
        logger.info(message)
        
        await event.bot.send_message(
            chat_id=event.chat_id,
            text='Регистрация чата прошла успешно!'
        )


@router.message_created(F.chat.type == 'chat')
async def what(event: MessageCreated):    
    chat_id: int = event.chat.chat_id
    user_id: int = event.from_user.user_id
    message: str = event.message.body.text
    date_send: datetime.datetime = datetime.datetime.fromtimestamp(event.timestamp / 1000)
    chat_title: str = event.chat.title
    
    formated_date_send: str = date_send.strftime("%Y-%m-%d %H:%M:%S")
    
    if 6 <= len(message) <= 256:
        result = await send_message_to_server(message=message, user_id=user_id, chat_title=chat_title[:32], chat_id=chat_id, date_send=formated_date_send)
        logger.info(result)


@router.bot_admin_permissions_changed()
async def on_permissions_changed(event: BotAdminPermissionsChanged):
    chat_id = event.chat_id    
    
    if event.is_admin and 'read_all_messages' in event.permissions:
        logger.info("Боту выдали права администратора в чате с возможностью чтения сообщений")
        await event.bot.send_message(
            chat_id=chat_id,
            text="🎉 Спасибо за права администратора! Теперь я вижу все сообщения в группе и готов сохранять ДЗ."
        )
    elif event.is_admin and 'read_all_messages' not in event.permissions:
        logger.info("Боту выдали права администратора в чате с возможностью чтения сообщений")
        await event.bot.send_message(
            chat_id=chat_id,
            text="🎉 Спасибо за права администратора, но вы не выдали разрешение на чтение сообщений"
        )
    else:
        logger.warning(f"У бота забрали права администратора в чате {chat_id}")
        await event.bot.send_message(
            chat_id=chat_id,
            text="⚠️ У меня забрали права администратора. Теперь я не могу отслеживать домашние задания."
        )