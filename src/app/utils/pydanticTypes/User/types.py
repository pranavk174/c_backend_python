from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AccountStatus(str, Enum):
    delete = "delete"
    DELETE = "DELETE"
    suspend = "suspend"
    SUSPEND = "SUSPEND"


class Email(BaseModel):
    email: str


class Otp(Email):
    otp: str


class verifyOtpInput(BaseModel):
    device_id: str
    ip_address: str
    location: str
    device_name: str
    email: str
    mobile: str | None
    otp: str


class User(Email):
    name: str
    id: int
    user_name: str
    bio: str
    mobile: str
    profile_pic: str
    chat_id: int
    cover_pic: str


class Users(BaseModel):
    items: list[User]


class VerifyOtpData(BaseModel):
    email: str
    id: int
    is_verified: bool


class UserInput(Email):
    fname: str
    lname: str
    user_name: str
    email: str
    bio: str = "Hey The!, I am using Whatsapp"
    mobile: str
    profile_pic: str | None = None
    cover_pic: str | None = None


class theme(str, Enum):
    dark = "dark"
    light = "light"


class UpdateUserInput(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    profile_pic: Optional[str] = None
    theme: Optional[str] = None


class blockUserInput(BaseModel):
    blocked_user_id: int
    reason: str | None = "no reason"
