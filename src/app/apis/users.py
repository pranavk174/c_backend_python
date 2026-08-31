from app.utils.pydanticTypes.User.types import (
    AccountStatus,
    UpdateUserInput,
    User,
    UserInput,
    blockUserInput,
    verifyOtpInput,
)

from ..utils.database import db
from ..utils.Apierros import AppError
from ..utils.Apiresponses import UserApiResponse, ApiResponse
from ..utils.utils import (
    otp_generator,
    async_util_handeler,
    generate_token,
    tokenValidator,
)
from ..helpers.apiutils import accountStatus, responseUpdate
from ..utils.emailsender import send_mail
from datetime import datetime, timedelta
from fastapi import BackgroundTasks, Request, Response
import asyncio
import bcrypt
import re
import random


from datetime import datetime, timezone

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


async def sendOtp(email: str):
    if not email:
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

    if len(existss) == 0:
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
            return

    else:
        # print(exists, "exists")
        exists = existss[0]
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
        message=f"Successfully Sent OTP Email {otp}", status=201, success=True
    )


async def verify_otp(data: verifyOtpInput, response: Response):

    otp = data.otp
    email = data.email

    print(email, otp)

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
        is_valid = bcrypt.checkpw(
            otp.encode("utf-8"), register[0]["otp"].encode("utf-8")
        )
        expires_at = register[0]["expires_at"]

        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

        if not is_valid or expires_at <= datetime.now(timezone.utc):
            raise AppError(
                message="OTP is Invalid Or Expiredddd", status=401, success=False
            )

        verified = await db.query_raw(
            """
            update register set is_verified = true where email = $1
""",
            email,
        )

        return UserApiResponse(
            message="Successfully Verified OTP",
            status=201,
            success=True,
            data={"email": email, "is_verified": True},
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
                message="OTP is Invalid Or Expiredss", status=401, success=False
            )
        else:
            print(
                expires_at,
                "expires at",
                datetime.now(timezone.utc),
                expires_at <= datetime.now(timezone.utc),
            )
            await responseUpdate(response, user[0], data)

            return UserApiResponse(
                message="Login successfull", status=201, success=True
            )


async def user_logout(data: User, response: Response):

    await db.query_raw(
        """
                              update devices set refresh_token = null , 
                              logged_out_at = $1::timestamptz 
                              where user_id = $2 and device_id = $3
                              
                              """,
        datetime.now(timezone.utc),
        data["id"],
        data["device_id"],
    )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("theme")

    return UserApiResponse(message="Logged out Successfully", status=200, success=True)


async def refresh_token(req: Request, response: Response):
    token = req.cookies.get("refresh_token")
    if not token:
        raise AppError(message="No refresh Token", status=401, success=False)
    print(token, "token in refresh")
    payload = tokenValidator(token, type="refresh")

    exists = await db.query_raw(
        """
                                select * from devices where device_id = $1 and user_id = $2 
                                """,
        payload["device_id"],
        payload["id"],
    )
    print(exists, "existss dataaa", payload["device_id"], payload["id"])
    if len(exists) == 0:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("theme")
        raise AppError(
            message="Token is Invalid or Revoked , Login Again",
            status=401,
            success=False,
        )
    # print(payload.user_id , "payload dataaaaaa")
    response.delete_cookie("access_token")
    access_token, refresh_token = generate_token(payload, payload["device_id"])
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
    )
    return UserApiResponse(
        message="Token refresh Successfully", status=201, success=True
    )


async def get_user_data(data: User):

    print(data, "dataaaaa user")
    user = await db.query_raw(
        """
                              
                              select * from users where account_status = $2::account_status and id = $1
                              
                              """,
        data["id"],
        "active",
    )

    return UserApiResponse(
        message="Successfully retrieved Users Data", status=200, data=user[0]
    )


async def get_all_users_data(data: User):
    users = await db.query_raw(
        """
                         SELECT
        u.*,
        MAX(cm.chat_id) AS chat_id
    FROM users u
   LEFT JOIN chat_member cm
    ON u.id = cm.member_id
    AND cm.chat_id IN (
        SELECT cm2.chat_id
        FROM chat_member cm2
        LEFT JOIN chat c
            ON c.id = cm2.chat_id
        WHERE cm2.member_id = $1
          AND c.chat_type = 'private'
    )
    
    WHERE u.id <> $1
    GROUP BY u.id;

""",
        data["id"],
    )

    return UserApiResponse(
        message="Successfully retrieved Users Data",
        ststus=200,
        success=True,
        data={"items": users},
    )


async def create_profile_api(input: UserInput):
    fname, lname, user_name, email, mobile, bio, profile_pic, cover_pic = (
        input.fname,
        input.lname,
        input.user_name,
        input.email,
        input.mobile,
        input.bio,
        input.profile_pic,
        input.cover_pic,
    )

    if not fname or not lname or not user_name or not email or not mobile:
        raise AppError(message="Input Field Missing", status=404, success=False)

    exists = await db.query_raw(
        """
                                    select * from users where email = $1
                                    """,
        email,
    )

    if len(exists) >= 1:
        raise AppError(message="User Already Exists Please login", status=400)

    isExists = await db.query_raw(
        """
                                select * from register where email = $1
                                """,
        email,
    )
    if len(isExists) == 0:
        data = await otp_generator()
        hashed_otp = data["hashed_otp"]
        otp = data["otp"]
        expires_at = data["expires_at"]
        # print(hashed_otp, otp, expires_at, "otp dataaaa", type(expires_at))
        await db.query_raw(
            """
            insert into register (email,otp,expires_at,is_verified) values ($1 ,$2,$3::timestamptz,false)
               
                """,
            email,
            hashed_otp,
            expires_at,
        )
        return UserApiResponse(
            message="User is not registered/verified OTP send Successfully",
            status=201,
            success=True,
        )

    await asyncio.gather(
        db.query_raw(
            """
                                    insert into users (name,user_name,email,mobile,bio,profile_pic, cover_pic) values($1,$2,$3,$4,$5,$6,$7)
                                    """,
            f"{fname} {lname}",
            user_name,
            email,
            mobile,
            bio,
            profile_pic,
            cover_pic,
        ),
        db.query_raw(
            """
            delete from register where email = $1
            
            """,
            email,
        ),
    )
    return UserApiResponse(message="Profile Created Success Fully", status=201)


async def update_profile_api(input: UpdateUserInput, data):
    update_data = input.model_dump(exclude_unset=True)
    if not update_data:
        raise AppError(message="Input field is missing", ststus=400)

    user_id = data["id"]

    allowed_fields = {"name", "email", "profile_pic", "theme", "bio"}
    update_data = {
        key: value for key, value in update_data.items() if key in allowed_fields
    }

    if not update_data:
        raise AppError(message="No valid fields to update", ststus=400)

    set_clause = ", ".join(
        f"{key} = ${index}" for index, key in enumerate(update_data.keys(), start=1)
    )

    values = list(update_data.values())
    values.append(user_id),
    user_id_placeholder = len(values)

    query = f"""
            update users set {set_clause} where id = ${user_id_placeholder} returning *

    """
    await db.query_raw(query, *values)

    return UserApiResponse(message="Successfully updated users", status=201)


async def account_delete_api(action_type: AccountStatus, data: User, res: Response):
    if not action_type:
        raise AppError(message="Action type missing", status=400)
    action = "deleted" if action_type == "delete" else "suspended"
    user = await db.query_raw(
        """
                        select * from users where id = $1
                            """,
        data["id"],
    )

    if len(user) == 0:
        raise AppError(message="User not found", status=404)

    if (
        user[0]["account_status"] == "deleted"
        or user[0]["account_status"] == "suspended"
    ):
        raise AppError(message=f"account is already {action_type}ed ", status=400)

    await db.query_raw(
        """
                        update users set account_status = $1::account_status where id = $2
                        """,
        action,
        data["id"],
    )
    res.delete_cookie("access_token")
    res.delete_cookie("refresh_token")
    res.delete_cookie("theme")
    return UserApiResponse(message=f"Sccueesfully {action} Account", status=201)


async def block_user_api(input: blockUserInput, data: User):
    if not input:
        raise AppError(message="Input field missing", status=400)
    if input.blocked_user_id == data["id"]:
        raise AppError(message="You Can not block your self", status=400)
    exists = await db.query_raw(
        """
                                
                                select * from users where id = $1
                                
                                """,
        input.blocked_user_id,
    )

    if len(exists) == 0:
        raise AppError(
            message="User does not exist!, You cannot blok this user", status=404
        )

    already_blocked = await db.query_raw(
        """
                                         select * from block where user_id = $1 and blocked_user_id = $2 and blocked = true and unblocked_at is NULL
                                         """,
        data["id"],
        input.blocked_user_id,
    )
    print(already_blocked, "already blocked ")
    if len(already_blocked) == 1:
        raise AppError(message="User Already blocked", status=400)

    await db.query_raw(
        """
                       
                       insert into block (user_id , blocked_user_id , blocked_at ,blocked,  reason) values($1,$2,$3::timestamptz,true,$4) 
                            
                            
                       """,
        data["id"],
        input.blocked_user_id,
        datetime.now(timezone.utc),
        input.reason,
    )

    return UserApiResponse(message="Successfully Blocked User", status=201)


async def unblock_user_api(input: int, data: User):
    if not input:
        raise AppError(message="Input field missing", status=400)
    if data["id"] == input:
        raise AppError(
            message="By mistake You Sent your id also to unblock you! Ha ha", status=400
        )
    exists = await db.query_raw(
        """
                                
                                select id from users where id = $1
                                
                                """,
        input,
    )

    if len(exists) == 0:
        raise AppError(
            message="User does not exist!, You cannot blok this user", status=404
        )

    already_blocked = await db.query_raw(
        """
                                         select * from block where user_id = $1 and blocked_user_id = $2 and blocked = false  and unblocked_at <> NULL
                                         """,
        data["id"],
        input,
    )
    if len(already_blocked) == 1:
        raise AppError(message="User Already unblocked", status=400)

    await db.query_raw(
        """
        
        update block set blocked = false ,unblocked_at= $3::timestamptz where user_id = $1 and blocked_user_id = $2 and unblocked_at is NULL 
                       
                    
                       """,
        data["id"],
        input,
        datetime.now(timezone.utc),
    )

    return UserApiResponse(message="Successfully unBlocked User", status=201)
