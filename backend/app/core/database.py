from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Shared SQLAlchemy metadata for every TableSwap module."""

    pass

engine = create_async_engine(str(settings.database_url), pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Provide one database session per request."""
    async with AsyncSessionLocal() as session:
        yield session
