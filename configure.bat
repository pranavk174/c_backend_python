
@echo off

echo ==============================
echo   FastAPI Project Setup
echo ==============================

echo.
echo Creating virtual environment...
call uv sync

echo.
echo Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Configuring Prisma Db
call uv run prisma db pull
call uv run prisma generate


echo.
echo starting server...
call uv run uvicorn src.main:app --reload


echo.
echo ==============================
echo   Setup Completed!
echo ==============================
echo.

pause