from maxapi import Router

from chat.chat import router as chat_router
from user.user import router as user_router

router = Router(router_id='main_router')
router.include_routers(
    chat_router,
    user_router
)