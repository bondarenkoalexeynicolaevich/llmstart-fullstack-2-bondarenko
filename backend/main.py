"""Точка входа ASGI: фабрика приложения и lifespan."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from backend.api.errors import ApiError, api_error_handler
from backend.api.router import router as v1_router
from backend.config import get_settings
from backend.database import dispose_database, get_engine, init_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    init_database(settings.database_url)
    async with get_engine().connect() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Backend started, database connection OK")
    yield
    await dispose_database()
    logger.info("Backend shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(title="Flow assistant backend", lifespan=lifespan)
    app.add_exception_handler(ApiError, api_error_handler)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(v1_router)
    return app


app = create_app()
