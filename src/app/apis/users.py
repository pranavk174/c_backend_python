from ..utils.database import db
from ..utils.Apierros import AppError
from ..utils.Apiresponses import UserApiResponse, ApiResponse
import random



from datetime import datetime, timezone








async def sendOtp(email:str):
    if not email:
       raise AppError("Something went wrong!",404,"Email is Missing")


    try:
        print("number")
        otp = random.randint(100000, 999999)
        timestamp = datetime.now(timezone.utc)
        print(str(timestamp) , "timestamp")
        exists = await db.query_raw(
    """
    SELECT *
    FROM users
    WHERE email = $1
    """,
    email
)
        if not exists:
            registered = await db.query_raw(

                """
        select * from register where email = $1 
""", 
email 
            )
            if not registered: 
                return ApiResponse(    message="Successfully Sent Email",
    status=201,
    success=True)
            
            return UserApiResponse(
    message="Successfully Sent Email",
    status=201,
    success=True,
    data=registered
)

    except Exception as error:
        raise error


    