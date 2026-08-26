from fastapi import APIRouter
from .userroute import user_router
from .chatroute import chat_router

base_router = APIRouter()

base_router.include_router(
    user_router
)
base_router.include_router(
    chat_router
)
