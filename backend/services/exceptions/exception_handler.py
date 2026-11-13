import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(name=__name__)


def handler_registrator(app: FastAPI):
    
    @app.exception_handler(SQLAlchemyError)
    async def func(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Функция-обработчик ошибок БД

        Args:
            request (Request): Объект запроса
            exc (SQLAlchemyError): Объект ошибки

        Returns:
            JSONResponse: Сообщение об ошибке
        """
        logger.error('Ошибка на стороне БД: %s', str(exc))
        
        return JSONResponse(
            content={'detail': 'Ошибка на стороне сервера. Пожалуйста, повторите запрос.'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )