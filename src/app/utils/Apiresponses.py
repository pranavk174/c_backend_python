from pydantic import BaseModel


class ApiResponse(BaseModel):
    message: str
    status: int
    success: bool
    error: str | None = None


class Email(BaseModel):
    email: str


class Otp(Email):
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


class UserApiResponse(ApiResponse):
      data: Users | User | VerifyOtpData 