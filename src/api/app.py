from contextlib import asynccontextmanager
from fastapi import FastAPI

from .trade.routers import router as trade_router


def create_app():

    app = FastAPI()

    app.include_router(trade_router)

    return app
