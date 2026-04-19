"""Async engine и фабрика сессий SQLAlchemy."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config import ASYNCPG_CONNECT_ARGS

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def init_database(database_url: str) -> None:
    global _engine, _session_maker
    _engine = create_async_engine(
        database_url,
        pool_pre_ping=True,
        connect_args=ASYNCPG_CONNECT_ARGS,
    )
    _session_maker = async_sessionmaker(_engine, expire_on_commit=False)


async def dispose_database() -> None:
    global _engine, _session_maker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_maker = None


def get_engine() -> AsyncEngine:
    if _engine is None:
        msg = "Database not initialized; call init_database() from lifespan"
        raise RuntimeError(msg)
    return _engine


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    if _session_maker is None:
        msg = "Database not initialized; call init_database() from lifespan"
        raise RuntimeError(msg)
    async with _session_maker() as session:
        yield session
