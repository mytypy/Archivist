import asyncio
import logging

from maxapi.types.chats import ChatMembersManager

logger = logging.getLogger(name=__name__)

async def get_ids_from_all_members(manager: ChatMembersManager) -> list[int] | list:
    members_id = []
    
    try:
        for attempt in range(1, 6):
            logger.info(f'Пробуем получить пользователей из чата. Попытка №{attempt}')
            
            async for member in manager.iter_all(count=30):
                if member.is_bot is False:
                    members_id.append(member.user_id)
                    
            break
                    
    except Exception:
        logger.exception('Ошибка при получении пользователей чата')
        
        members_id.clear()
        await asyncio.sleep(2)
    
    return members_id