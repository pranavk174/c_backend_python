from ..utils.database import db
from ..utils.Apierros import AppError
from ..utils.Apiresponses import UserApiResponse, ApiResponse
from ..utils.utils import otp_generator
import random


from datetime import datetime, timezone


async def sendOtp(email: str):
    if not email:
        raise AppError("Something went wrong!", 404, "Email is Missing")

    try:
        print("number")

        data = await otp_generator()

        hashed_otp = data["hashed_otp"]
        otp = data["otp"]
        expires_at = data["expires_at"]
        print(hashed_otp, otp, expires_at, "otp dataaaa", type(expires_at))
        timestamp = datetime.now(timezone.utc)
        print(str(timestamp), "timestamp")
        existss = await db.query_raw(
            """
    SELECT *
    FROM users
    WHERE email = $1 limit 1
    """,
            email,
        )

        exists = existss[0]
        if not exists:
            registered = await db.query_raw(
                """
        select * from register where email = $1  
""",
                email,
            )
            if registered:
                await db.query_raw(
                    """
        UPDATE register
        SET otp = $1,
            expires_at = $2::timestamptz
        WHERE email = $3
        """,
                    hashed_otp,
                    expires_at,
                    email,
                )
            else:
                await db.query_raw(
                    """

insert into register (email,otp,expires_at,is_verified) values ($1 ,$2,$3::timestamptz,false)
   
    """,
                    email,
                    hashed_otp,
                    expires_at,
                )

        else:
            print(exists, "exists")
            if (
                exists["account_status"] == "deleted"
                or exists["account_status"] == "suspended"
            ):
                raise AppError(
                    message=f"Account is {exists.account_status}, contact support",
                    status_code=403,
                    success=False,
                )
            else:
                await db.query_raw(
                    """
                    update otp set otp = $1 , expires_at = $2::timestamptz where email = $3
                    
                    """,
                    hashed_otp,
                    expires_at,
                    email,
                )

            return ApiResponse(
                message="Successfully Sent OTP Email", status=201, success=True
            )
    except Exception as error:

        raise AppError(
            message="something went wrong", status=500, error=error, success=False
        )
