import bcrypt
from datetime import datetime, timedelta
import secrets


async def otp_generator():
    expires_at = datetime.now() + timedelta(minutes=5)

    otp = 100000 + secrets.randbelow(900000)

    hashed_otp = bcrypt.hashpw(str(otp).encode(), bcrypt.gensalt()).decode()

    return {
        "hashed_otp": hashed_otp,
        "otp": otp,
        "expires_at": expires_at,
    }
