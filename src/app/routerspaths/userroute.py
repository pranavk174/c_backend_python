from fastapi import APIRouter, Depends, Response


from app.middlewares.auth import is_logged_in
from app.utils.pydanticTypes.User.types import verifyOtpInput
from ..apis.users import get_user_data, sendOtp as send_otp, user_logout, verify_otp
from ..utils.utils import asyncHandeler

user_router = APIRouter()


@user_router.get("/")
async def get_data():
    return {"success": "true"}


@user_router.post("/send-otp")
@asyncHandeler
async def send_otp_route(email: str):
    return await send_otp(email)


@user_router.post("/verify-otp")
@asyncHandeler
async def oTpVerify(data: verifyOtpInput, response: Response):
    return await verify_otp(data, response)


@user_router.post("/logout")
@asyncHandeler
async def logout(response: Response, data=Depends(is_logged_in)):
    print(type(data), "type===")
    return await user_logout(data, response)


@user_router.get("/get-user")
@asyncHandeler
async def get_user(data=Depends(is_logged_in)):
    print(type(data), "type===")
    return await get_user_data(data)
