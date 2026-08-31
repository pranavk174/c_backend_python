from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.utils.Apierros import AppError
from .userroute import user_router
from .chatroute import chat_router

base_router = APIRouter()



base_router.include_router(user_router, prefix="/user")
base_router.include_router(chat_router, prefix="/chat")
