import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from api.routes.message.message import router as message_router
from db.manager import cfg
from services.my_redis.redis import redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s:%(lineno)d] %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):    
    try:
        await cfg.wait_db(retries=10, delay=2)
        await redis.init(retries_for_ping=10)
        
        yield
    
    finally:
        await cfg.dispose()

app = FastAPI(lifespan=lifespan)


api = APIRouter(prefix='/api')

api.include_router(message_router)

app.include_router(api)