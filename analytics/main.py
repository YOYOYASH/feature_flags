from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from .database.connection import db
from .routes import router
import uvicorn
from logging_config import setup_logging
import logging

@asynccontextmanager
async def lifespan(app:FastAPI):
    setup_logging()
    await db.connect()
    yield
    await db.disconnect()


app =FastAPI(lifespan=lifespan)

logger = logging.getLogger("app")

@app.middleware("http")
async def log_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception(
            "unhandled_exception",
            extra={
                "context": {
                    "path": request.url.path,
                    "method": request.method,
                    "tenant_id": getattr(request.state, "tenant_id", None),
                    "principal_id": getattr(request.state, "id", None),
                }
            }
        )
        raise

app.include_router(router)




if __name__ == '__main__':
    uvicorn.run("analytics.main:app",host='127.0.0.1',port=8082,reload=True)