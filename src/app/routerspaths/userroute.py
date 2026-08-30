from fastapi import APIRouter, Depends, Request, Response


from app.middlewares.auth import is_logged_in
from app.utils.pydanticTypes.User.types import (
    AccountStatus,
    UpdateUserInput,
    UserInput,
    blockUserInput,
    verifyOtpInput,
)
from ..apis.users import (
    account_delete_api,
    block_user_api,
    create_profile_api,
    get_all_users_data,
    get_user_data,
    refresh_token,
    sendOtp as send_otp,
    unblock_user_api,
    update_profile_api,
    user_logout,
    verify_otp,
)
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


@user_router.post("/create_profile")
@asyncHandeler
async def create_profile(data: UserInput):
    return await create_profile_api(data)


@user_router.put("/update_profile")
@asyncHandeler
async def update_profile(input: UpdateUserInput, data=Depends(is_logged_in)):
    return await update_profile_api(input, data)


@user_router.post("/refresh-token")
@asyncHandeler
async def refresh_token_api(request: Request, response: Response):
    return await refresh_token(request, response)


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


@user_router.get("/get-users")
@asyncHandeler
async def get_user(data=Depends(is_logged_in)):
    return await get_all_users_data(data)


@user_router.patch("/deactivate-account")
@asyncHandeler
async def delete_account(
    action_type: AccountStatus, res: Response, data=Depends(is_logged_in)
):
    return await account_delete_api(action_type, data, res)


@user_router.post("/block-user")
@asyncHandeler
async def block_user(input: blockUserInput, data=Depends(is_logged_in)):
    return await block_user_api(input, data)


@user_router.post("/unblock-user")
@asyncHandeler
async def unblock_user(input: blockUserInput, data=Depends(is_logged_in)):
    return await unblock_user_api(input.blocked_user_id, data)
