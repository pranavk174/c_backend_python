from pydantic import BaseModel
from typing import Optional


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
