from ..utils.database import db
from ..utils.Apierros import AppError
from ..utils.Apiresponses import UserApiResponse, ApiResponse
from ..utils.utils import otp_generator, async_util_handeler, generate_token
from ..helpers.apiutils import accountStatus, responseUpdate
from ..utils.emailsender import send_mail
from datetime import datetime, timedelta
from fastapi import Response
import bcrypt
import re
import random


from datetime import datetime, timezone

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


async def sendOtp(email: str):
    if not email or not re.match(EMAIL_REGEX, email):
        raise AppError("Something went wrong!", 404, "Email is Missing")

    print("number")

    data = await otp_generator()

    hashed_otp = data["hashed_otp"]
    otp = data["otp"]
    expires_at = data["expires_at"]
    # print(hashed_otp, otp, expires_at, "otp dataaaa", type(expires_at))
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
        # print(exists, "exists")
        accountStatus(exists)
        data = await db.query_raw(
            """
                    INSERT INTO otp (email, otp, expires_at)
    VALUES ($1, $2, $3::timestamptz)
    ON CONFLICT (email)
    DO UPDATE SET
        otp = EXCLUDED.otp,
        expires_at = EXCLUDED.expires_at
    RETURNING *
                    """,
            email,
            hashed_otp,
            expires_at,
        )
        print(
            otp,
            "inserted ddataaaaa",
            hashed_otp,
            expires_at,
            email,
        )

        await async_util_handeler(
            send_mail(to_email=email, body=otp, subject="Otp Verification")
        )

        return ApiResponse(
            message="Successfully Sent OTP Email", status=201, success=True
        )


async def verify_otp(otp: str, email: str, response: Response, **args: dict):
    if len(otp) != 6 or not email or not re.match(EMAIL_REGEX, email):
        print((len(otp) != 6 or not email or re.match(EMAIL_REGEX, email)), "condition")
        raise AppError(
            message="Email or OTP is Missing", status=404, success=False, error="error"
        )
    user = await db.query_raw(
        """
        SELECT * FROM users where email = $1
""",
        email,
    )
    if len(user) != 1:
        register = await db.query_raw(
            """
            select * from register where email = $1
""",
            email,
        )
        if len(register) == 0:
            raise AppError(message="User Does not exist", status=404, success=False)
        is_valid = bcrypt.checkpw(otp.encode("utf-8"), register[0]["otp"])
        if not is_valid or register[0]["expires_at"] <= datetime.now():
            raise AppError(
                message="OTP is Invalid Or Expired", status=401, success=False
            )

        verified = await db.query_raw(
            """
            update table register set is_verified = true where email = $1
""",
            email,
        )

        return ApiResponse(
            message="Successfully Verified OTP",
            status=201,
            success=True,
            data={"email": {email}, "is_verified": True},
        )
    else:
        accountStatus(user[0])

        otpDetails = await db.query_raw(
            """
                    select * from otp where email = $1
        """,
            email,
        )
        if len(otpDetails) == 0:
            raise AppError(
                message=f"OTP dies nt exist in the ser Id Please Send Again",
                status=403,
                success=False,
            )
        is_valid = bcrypt.checkpw(
            otp.encode("utf-8"), otpDetails[0]["otp"].encode("utf-8")
        )
        expires_at = otpDetails[0]["expires_at"]

        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

        if not is_valid or expires_at <= datetime.now(timezone.utc):

            raise AppError(
                message="OTP is Invalid Or Expired", status=401, success=False
            )
        else:
            print(
                expires_at,
                "expires at",
                datetime.now(timezone.utc),
                expires_at <= datetime.now(timezone.utc),
            )
            await responseUpdate(response, email, user[0], **args)

            return UserApiResponse(
                message="Login successfull", status=201, success=True
            )
