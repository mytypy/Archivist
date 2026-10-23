from hmac import compare_digest

from fastapi import HTTPException, Request, status

from core.config import AppSettings


async def is_bot(request: Request):
    """Зависимость, которая проверяет секретный токен приложения

    Args:
        request (Request): Объект запроса

    Raises:
        HTTPException: Ошибка, если передан невалидный токен
    """
    
    app_settings = AppSettings()
    
    secret_bot_token: str | None = request.headers.get(app_settings.SECRET_HEADER, '')
    
    if not compare_digest(secret_bot_token, app_settings.SECRET_TOKEN):
        raise HTTPException(detail='Невалидный токен!', status_code=status.HTTP_403_FORBIDDEN)