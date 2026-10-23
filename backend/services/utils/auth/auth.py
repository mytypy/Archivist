from services.my_redis.redis import redis


async def get_user_cache(max_id: int) -> int | None:
    """Функция для проверки пользователя из кэша

    Args:
        user_id (int): ID пользователя

    Returns:
        int: Значение ID
    """
    
    key = f'user:{max_id}'
    data = await redis.get(name=key)
    
    return data


async def get_chat_cache(chat_max_id: int) -> int | None:
    """Функция для проверки чата из кэша

    Args:
        chat_id (int): ID чата

    Returns:
        int: Значение ID
    """
    
    key = f'chat:{chat_max_id}'
    data = await redis.get(name=key)
    
    return data


async def get_user_chat(max_id: int, chat_max_id: int) -> int | None:
    """Функция для получения user_chat из кэша

    Args:
        user_id (int): ID пользователя
        chat_id (int): ID чата

    Returns:
        int: Значение ID
    """
    
    key = f'user:{max_id}chat:{chat_max_id}'
    data = await redis.get(name=key)
    
    return data


async def set_user_cache(max_id: int, user_id: int, ex_min: int = 60 * 24) -> int | None:
    """Функция, для создания пользователя в кэше

    Args:
        user_id (int): ID пользователя
        user_id (int): Значение кэша (user ID)
        ex_min (int, optional): Время жизни ключа. По умолчанию 24 часа = 1440 минут

    Returns:
        int: Значение ID
    """
    
    key = f'user:{max_id}'
    data = await redis.set(name=key, value=user_id, ex=ex_min)
    
    return data


async def set_chat_cache(chat_max_id: int, chat_id: int, ex_min: int = 60 * 24) -> int | None:
    """Функция, для создания чата в кэше

    Args:
        chat_id (int): ID чата
        chat_id (int): Значение кэша (chat_id ID)
        ex_min (int, optional): Время жизни ключа. По умолчанию 24 часа = 1440 минут

    Returns:
        int: Значение ID
    """
    
    key = f'chat:{chat_max_id}'
    data = await redis.set(name=key, value=chat_id, ex=ex_min)
    
    return data


async def set_user_chat(max_id: int, chat_max_id: int, user_chat_id: int, ex_min: int = 60 * 24) -> int | None:
    """Функция, для создания user_chat в кэше

    Args:
        user_id (int): ID пользователя
        chat_id (int): ID чата
        user_chat_id (int): Значение кэша (user_chat ID)
        ex_min (int, optional): Время жизни ключа. По умолчанию 24 часа = 1440 минут

    Returns:
        int: Значение ID
    """
    
    key = f'user:{max_id}chat:{chat_max_id}'
    data = await redis.set(name=key, value=user_chat_id, ex=ex_min)
    
    return data