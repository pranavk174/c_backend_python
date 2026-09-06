from fastapi import Cookie, Depends, HTTPException, Request

from app.utils.Apierros import AppError
from app.utils.utils import tokenValidator
from app.utils.database import db

async def is_logged_in(access_token: str | None = Cookie(default=None)):
    token = access_token
    if not token:
        raise HTTPException(
            detail="User is not logged in ,Access Token is missing", status_code=401
        )
    
    payload = tokenValidator(token, type="access")

    return payload


async def is_chat_member(chat_id:int,data = Depends(is_logged_in)):
     if not chat_id:
         raise AppError(
                      message = "Chat Id Missing",status=400,success= False
                  )
     chat = await db.query_raw("""
   
   select * from chat where id = $1 and is_deleted = false
   
   """,chat_id)

     if(len(chat)== 0):
         raise AppError(
             message = "Chat does not Exists",status=404,success= False
         )

     is_member = await db.query_raw("""

                    select * from chat_member where member_id = $1 and chat_id = $2
""", data['id'],chat_id )

     if(len(is_member) == 0):
         raise AppError(
                      message = "You Are not member of this chat",status=400,success= False
                  )
     return data

    
     
