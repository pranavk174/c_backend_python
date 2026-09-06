from enum import Enum
from pydantic import BaseModel
from typing import Optional

from app.utils.Apiresponses import ApiResponse


class delete_type(str,Enum):
  onlyme = "onlyme"
  ONLYME ="ONLYME"
  OnlyMe = "OnlyMe"
  Everyone = "Everyone"
  everyone = "everyone"
  EVERYONE = "EVERYONE"
from pydantic import BaseModel
from typing import Optional, List, Union


class Chats(BaseModel):
    chat_id: int
    user_id: Optional[int] = None
    profile_pic: Optional[str] = None
    cover_pic: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[str] = None
    blocked: Optional[bool] = None
    isOnline: Optional[bool] = None
    name: str
    chat_type: str
    unread_count: int
    bio: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None


class Emoji(BaseModel):
    react_id: int
    emoji: str


class Emojis(BaseModel):
    items: List[Emoji]


class Reaction(BaseModel):
    react_id: int
    user_id: int


class Chat(BaseModel):
    id: int
    sender_id: int
    created_at: str
    seen_at: Optional[str] = None
    is_forwarded: bool
    preview: Optional[str] = None
    content: Optional[str] = None
    seen_users: Optional[List[Optional[int]]] = None
    story_id: Optional[int] = None
    story_item: Optional[str] = None
    is_edited: bool
    reply_to_message_id: Optional[int] = None
    is_deleted: Optional[bool] = None
    reactions: List[Reaction]


class Message(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    content: str
    created_at: str


class SingleChat(BaseModel):
    items: Optional[List[Chat]] = None
    has_more: bool 
    next_cursor: Optional[int] = None



class AllChats(BaseModel):
    items: Optional[List[Chats]] = None


class Wallpaper(BaseModel):
    url: str


class NewChat(BaseModel):
    chat_id: int


class Member(BaseModel):
    member_id: int
    role: str


class Members(BaseModel):
    items: List[Member]

ChatResponse = Union[
    SingleChat,
    AllChats,
    Emojis,
    Wallpaper,
    NewChat,
    Members,
]

class ChatApiResponse(ApiResponse):
    data: Optional[ChatResponse] = None
