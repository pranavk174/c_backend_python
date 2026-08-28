from fastapi import HTTPException, Request

from app.utils.utils import tokenValidator


async def is_logged_in(req: Request):
    token = req.cookies.get("access_token")
    if not token:
        raise HTTPException(
            detail="User is not logged in ,Access Token is missing", status_code=401
        )
    payload = tokenValidator(token, type="access")

    return payload
