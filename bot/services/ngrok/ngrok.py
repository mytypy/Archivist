import ngrok

from utils.config.config import get_bot_settings


async def main_ngrok_service_manager(port: int, url: str):
    settings = get_bot_settings()
       
    listener = ngrok.forward(
        addr=port,
        authtoken=settings.NGROK_TOKEN,
        domain=url
    )
    
    task = await listener
    
    return task.url()