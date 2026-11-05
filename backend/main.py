import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse

from api.routes.message.message import router as message_router
from db.manager import cfg
from services.exceptions.exception_handler import handler_registrator
from services.my_redis.my_redis import redis
from services.requests.request import check_llm_service
from services.requests.request_client import request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s:%(lineno)d] %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):    
    try:
        await request.init(retries=10)
        # await check_llm_service(delay=10.0)
        await cfg.wait_db(retries=10, delay=2)
        await redis.init(retries_for_ping=10)
        
        yield
    
    finally:
        await cfg.dispose()
        await request.close()

app = FastAPI(lifespan=lifespan)
# handler_registrator(app=app)

api = APIRouter(prefix='/api')


@api.get('/health/')
async def is_health() -> JSONResponse:
    """Функция для проверки работы сервиса

    Returns:
        JSONResponse: Ответ, если все ок
    """
    
    return JSONResponse(
        content={'response': 'I\'m Okay'},
        status_code=status.HTTP_200_OK
    )
    
    
api.include_router(message_router)

app.include_router(api)