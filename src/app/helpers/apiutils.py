from fastapi import Response
from ..utils.database import db
from ..utils.Apiresponses import User
from ..utils.Apierros import AppError
from ..utils.utils import generate_token
from datetime import datetime, timedelta, timezone


async def responseUpdate(response: Response, email, user: User, **args: dict):
    access_token, refresh_token = generate_token(user)
    print("=========", args, "argsssss")

    args = args["args"]

    email, otp, device_id, ip_address, location, device_name = args.values()
    await db.query_raw(
        """
                        
                       insert into devices (device_id,ip_address,location,device_name,expires_at,last_login,user_id,refresh_token) values($1,$2,$3,$4,$5::timestamptz,$6::timestamptz,$7,$8)
                       on conflict(user_id,device_id)
                       do update set
                                 expires_at = EXCLUDED.expires_at,
        last_login = EXCLUDED.last_login,
        ip_address = EXCLUDED.ip_address,
        location = EXCLUDED.location,
        refresh_token = EXCLUDED.refresh_token
    
                       """,
        device_id,
        ip_address,
        location,
        device_name,
        datetime.now(timezone.utc) + timedelta(days=7),
        datetime.now(timezone.utc),
        user["id"],
        refresh_token,
    )
    await db.query_raw(
        """
                                               
                    delete  from otp where email = $1 
                                               
                    """,
        email,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
    )
    response.set_cookie(key="theme", value=user["theme"])


def accountStatus(user):
    if user["account_status"] == "deleted" or user["account_status"] == "suspended":
        raise AppError(
            message=f"Account is {user.account_status}, contact support",
            status_code=403,
            success=False,
        )
