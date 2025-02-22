from contextlib import asynccontextmanager
from fastapi import FastAPI

from .trade.routers import router as trade_router
from cache.reddis_client import redis_client


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await redis_client.connect()
        yield
        await redis_client.disconnect()

    app = FastAPI(lifespan=lifespan)

    app.include_router(trade_router)

    return app
