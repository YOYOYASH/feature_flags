from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database.connection import db
from .routes import router
import uvicorn


@asynccontextmanager
async def lifespan(app:FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app =FastAPI(lifespan=lifespan)

app.include_router(router)


if __name__ == '__main__':
    uvicorn.run("control_pane.main:app",host='127.0.0.1',port=8080,reload=True)
