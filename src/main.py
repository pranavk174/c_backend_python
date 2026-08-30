import os

from fastapi import FastAPI
from app.utils.database import lifespan
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


from app.routerspaths.baseroute import base_router

load_dotenv()


app = FastAPI(title="Chat API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(base_router, prefix="/api/v1")
