import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.utils.Apierros import (
    AppError,
    app_error_handler,
    generic_handler,
    type_error_handler,
    validation_error_handler,
)
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


app.exception_handler(AppError, app_error_handler)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)
app.exception_handler(TypeError, type_error_handler)

app.exception_handler(Exception, generic_handler)


app.include_router(base_router, prefix="/api/v1")
