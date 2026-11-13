import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse

from agents.checker import check_model
from api.routes.models import router as model_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s:%(lineno)d] %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Главная функция для запуска сервера, если модель прогрелась

    Args:
        app (FastAPI): Объект приложения
    """
    
    try:
        await check_model(delay=1)
        
        yield
    finally:
        pass
    
    
app = FastAPI(lifespan=lifespan)

api = APIRouter(prefix='/api')


@app.get('/health/')
async def is_health() -> JSONResponse:
    """Функция для проверки работы сервиса

    Returns:
        JSONResponse: Ответ, если модель прогрета
    """
    
    return JSONResponse(
        content={'response': 'I\'m Okay'},
        status_code=status.HTTP_200_OK
    )
    

api.include_router(model_router)
app.include_router(api)