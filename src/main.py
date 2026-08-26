import os

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .app.apis.users import sendOtp as send_otp 
from prisma import Prisma
from .app.utils.database import lifespan
load_dotenv()


app = FastAPI(
    title="Chat API",
    lifespan=lifespan
)






app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():

  users = await db.users.find_many()

  print(users)

  return {"todos":users}



@app.post('/send-otp')
async def send_otp_route(email: str):
    print(email, "email dataaaa")
    return await send_otp(email)

 