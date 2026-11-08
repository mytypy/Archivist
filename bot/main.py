import asyncio
import logging

from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, Command, MessageCreated

from constants.messages import START_MESSAGE
from keyboard.keyboard import ask_question_buttons
from main_router import router as main_router
from services.ngrok.ngrok import main_ngrok_service_manager
from services.requests.request_client import request
from services.requests.request import check_backend_service
from utils.config.config import get_bot_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s:%(lineno)d] %(levelname)s %(message)s",
)
logger = logging.getLogger(name=__name__)

dp = Dispatcher()   
dp.include_routers(
    main_router
)

    
@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=START_MESSAGE,
        attachments=[
            await ask_question_buttons()
        ]
    )


@dp.message_created(Command('start'))
async def start_in_chat(event: MessageCreated):
    await event.message.answer(
        text=START_MESSAGE,
        attachments=[
            await ask_question_buttons()
        ]
    )
    
    
async def main():
    try:
        await request.init(retries=10)
        await check_backend_service(delay=3.0)
        
        PORT = 8080  # Единый порт для ngrok и вебхука
        settings = get_bot_settings()

        url = await main_ngrok_service_manager(port=PORT, url=settings.NGROK_URL)
        
        bot = Bot(token=settings.TOKEN)
        await bot.subscribe_webhook(url=url, secret=settings.TOKEN)
        
        await dp.handle_webhook(
            bot=bot, 
            host='127.0.0.1',   
            port=PORT,
            log_level='critical',
            secret=settings.TOKEN
        )
    except Exception as er:
        await request.close()


if __name__ == '__main__':
    asyncio.run(main())