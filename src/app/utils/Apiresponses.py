from pydantic import BaseModel
from typing import Optional

from app.utils.pydanticTypes.User.types import Users, User, VerifyOtpData


class ApiResponse(BaseModel):
    message: str
    status: int = 200
    success: bool = True
    error: str | None = None


class UserApiResponse(ApiResponse):
    data: Users | User | VerifyOtpData | Optional[dict] = None
