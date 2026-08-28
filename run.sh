echo
echo "Installing dependencies..."
uv sync

echo
echo "Starting server..."
uv run uvicorn src.main:app --reload