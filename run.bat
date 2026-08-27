echo.
echo Activating virtual environment...
call .venv\Scripts\activate

echo.
echo starting server...
call uv run uvicorn src.main:app --reload

