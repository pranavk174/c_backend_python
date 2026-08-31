from fastapi import APIRouter, Depends, Path, Query, Request, Response


from app.middlewares.auth import is_logged_in
from app.utils.Apiresponses import UserApiResponse
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
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


@user_router.get("/")
async def get_data():
    return {"success": "true"}

# path  parameter
@user_router.post("/send-otp/{email}", response_model=UserApiResponse)

async def send_otp_route(email: str = Path(pattern=EMAIL_REGEX)):
    return await send_otp(email)


@user_router.post("/verify-otp",response_model=UserApiResponse)

async def oTpVerify(data: verifyOtpInput, response: Response):
    return await verify_otp(data, response)


@user_router.post("/create_profile", response_model=UserApiResponse)

async def create_profile(data: UserInput):
    return await create_profile_api(data)


@user_router.put("/update_profile", response_model=UserApiResponse)

async def update_profile(input: UpdateUserInput, data=Depends(is_logged_in)):
    return await update_profile_api(input, data)


@user_router.post("/refresh-token", response_model=UserApiResponse)

async def refresh_token_api(request: Request, response: Response):
    return await refresh_token(request, response)


@user_router.post("/logout", response_model=UserApiResponse)

async def logout(response: Response, data=Depends(is_logged_in)):
    print(type(data), "type===")
    return await user_logout(data, response)


@user_router.get("/get-user", response_model=UserApiResponse)

async def get_user(data=Depends(is_logged_in)):
    print(type(data), "type===")
    return await get_user_data(data)


@user_router.get("/get-users", response_model=UserApiResponse)

async def get_user(data=Depends(is_logged_in)):
    return await get_all_users_data(data)


@user_router.patch("/deactivate-account", response_model=UserApiResponse)

async def delete_account(
    action_type: AccountStatus, res: Response, data=Depends(is_logged_in)
):
    return await account_delete_api(action_type, data, res)


@user_router.post("/block-user", response_model=UserApiResponse)

async def block_user(input: blockUserInput, data=Depends(is_logged_in)):
    return await block_user_api(input, data)


@user_router.post("/unblock-user", response_model=UserApiResponse)

async def unblock_user(input: blockUserInput, data=Depends(is_logged_in)):
    return await unblock_user_api(input.blocked_user_id, data)
