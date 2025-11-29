from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import db


@asynccontextmanager
async def lifespan(app:FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app =FastAPI(lifespan=lifespan)


