from fastapi import APIRouter
from ..apis.users import sendOtp as send_otp

user_router = APIRouter()


@user_router.get("/")
async def get_data():
    return {"success": "true"}


@user_router.post("/send-otp")
async def send_otp_route(email: str):
    print(email, "email dataaaa")
    return await send_otp(email)
