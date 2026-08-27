

echo "=============================="
echo "  FastAPI Project Setup"
echo "=============================="

echo
echo "Installing dependencies..."
uv sync



echo
echo "Configuring Prisma DB..."
uv run prisma db pull
uv run prisma generate

echo
echo "Starting server..."
uv run uvicorn src.main:app --reload