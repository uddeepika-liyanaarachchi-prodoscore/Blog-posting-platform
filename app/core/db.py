from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# create the database connection
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# create a session everytime 
AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False,expire_on_commit=False)

# create db tables
Base = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()