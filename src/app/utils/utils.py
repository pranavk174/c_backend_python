import bcrypt
from datetime import datetime, timedelta, timezone
import secrets
from .Apierros import AppError
import traceback


async def otp_generator():
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    otp = 100000 + secrets.randbelow(900000)

    hashed_otp = bcrypt.hashpw(str(otp).encode(), bcrypt.gensalt()).decode()

    return {
        "hashed_otp": hashed_otp,
        "otp": otp,
        "expires_at": expires_at,
    }


from functools import wraps
from fastapi import HTTPException
from fastapi.responses import JSONResponse


def asyncHandeler(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)

        except AppError as er:
            return JSONResponse(
                status_code=er.status,
                content={
                    "success": er.success,
                    "message": er.message,
                    "error": er.error,
                    "status": er.status,
                },
            )
        except HTTPException:
            raise

        except Exception as er:

            print(er, "error===========")

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Internal Server Error",
                    "error": {er},
                },
            )

    return wrapper


async def async_util_handeler(fn):
    try:
        return await fn

    except AppError as er:
        print(er, "error in ")
        raise AppError(
            message="Something Went Wrong",
            status=er.status,
            success=er.success,
            # error={er.message}
        )
    except Exception as er:
        print(er, "error in =====================")
        traceback.print_exc()
        raise AppError(
            message="Something went wrong", status=500, error=str(er), success=False
        ) from er


import os
import jwt

jwt_secret = os.getenv("JWT_SECRET")
jwt_algo = "HS256"


def generate_token(user):
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    access_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload = {
        "user_id": user["id"],
        "profile_pic": user["profile_pic"],
        "email": user["email"],
    }

    access_payload = {
        **payload,
        "exp": access_expires_at,
    }

    refresh_payload = {
        **payload,
        "exp": refresh_expires_at,
    }

    access_token = jwt.encode(access_payload, jwt_secret, algorithm=jwt_algo)
    refresh_token = jwt.encode(refresh_payload, jwt_secret, algorithm=jwt_algo)

    return access_token, refresh_token
