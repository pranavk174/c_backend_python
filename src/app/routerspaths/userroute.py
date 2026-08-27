from fastapi import APIRouter, Response
from ..apis.users import sendOtp as send_otp, verify_otp
from ..utils.utils import asyncHandeler

user_router = APIRouter()


@user_router.get("/")
async def get_data():
    return {"success": "true"}


@user_router.post("/send-otp")
@asyncHandeler
async def send_otp_route(email: str):
    print(email, "email dataaaa")
    return await send_otp(email)


@user_router.post("/verify-otp")
@asyncHandeler
async def oTpVerify(otp: str, email: str, response: Response, **args: dict):
    return await verify_otp(otp, email, response, **args)
