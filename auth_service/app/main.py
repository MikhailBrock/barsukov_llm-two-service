from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import router
from app.core.exceptions import BaseHTTPException
from app.db.session import engine
from app.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Auth Service", lifespan=lifespan)


@app.exception_handler(BaseHTTPException)
async def http_exception_handler(request: Request, exc: BaseHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
