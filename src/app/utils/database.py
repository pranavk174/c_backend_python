from prisma import Prisma
from contextlib import asynccontextmanager
from fastapi import FastAPI
db = Prisma()
@asynccontextmanager

async def lifespan(app: FastAPI):
    # Server start hone par
    await db.connect()

    yield

    # Server shutdown hone par
    await db.disconnect()
