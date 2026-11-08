from maxapi.types import ButtonsPayload, CallbackButton, MessageButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


async def chats_button(data: list[dict]):
    builder = InlineKeyboardBuilder()
    
    for i in data[:3]:
        builder.row(
            CallbackButton(
                text=i['title'],
                payload=str(i['chat_id']),
            ),
            CallbackButton(
                text='Главное меню',
                payload='Главное меню',
            ),
        )
    
    return builder.as_markup()


async def ask_question_buttons():
    buttons = [
            [
            MessageButton(text="Узнать ДЗ")
            ],
        ]
    
    buttons_payload = ButtonsPayload(buttons=buttons).pack()
    
    return buttons_payload


async def go_back():
    buttons = [
            [
            MessageButton(text="Главное меню")
            ],
        ]
    
    buttons_payload = ButtonsPayload(buttons=buttons).pack()
    
    return buttons_payload