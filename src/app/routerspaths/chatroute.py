from fastapi import APIRouter, Depends

from app.apis.chats import create_chat, get_chat_by_id
from app.middlewares.auth import is_chat_member, is_logged_in
from app.utils.pydanticTypes.Chat.types import ChatApiResponse

chat_router = APIRouter(dependencies=[Depends(is_logged_in)])


@chat_router.get("/get-single-chat/{chat_id}", response_model=ChatApiResponse)
async def get_single_chat(
    chat_id: int, next_cursor: int | None = None, data=Depends(is_chat_member)
):
    return await get_chat_by_id(chat_id, next_cursor, data, limit=20)


@chat_router.post("/new-chat", response_model=ChatApiResponse)
async def create_new_chat(member_id: int, data=Depends(is_logged_in)):
    return await create_chat(member_id, data)
