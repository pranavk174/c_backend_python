from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

is_dev = os.getenv("DEV_ENV") == "development"


class AppError(Exception):
    def __init__(
        self, message: str, status: int, error: str | None = None, success: bool = False
    ):
        self.message = message
        self.status = status
        self.error = error
        self.success = success
        super().__init__({"message": message, "status": status, "success": success})


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    print(exc, "exception in validation")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "status": 422,
            "errors": exc.errors(),
        },
    )


async def type_error_handler(request: Request, er: TypeError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Something Went wrong",
            "status": 422,
            "error": str(er),
        },
    )


async def generic_handler(request: Request, er: Exception):
    print(er, "exception in exception")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": str(er) if is_dev else "Something Went wrong",
            "status": 500,
            # "error": str(er),
        },
    )


async def app_error_handler(request: Request, er: AppError):
    print(er, "exception ")
    return JSONResponse(
        status_code=er.status,
        content={
            "success": False,
            "message": er.message,
            "status": er.status,
            # "error": str(er.error),
        },
    )
