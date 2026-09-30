from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.exceptions import InvalidPasswordException, UserAlreadyExistsException, user_already_exists_handler ,username_password_invalicd_handler
from app.routers.router import api_router
from app.core.db import AsyncSessionLocal, engine, Base
from app.core.seed import seed_initial_admin
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def init_mysql_database():
    db_url = settings.DATABASE_URL
    base_url, db_name = db_url.rsplit("/", 1)
    
    temp_engine = create_async_engine(f"{base_url}/", isolation_level="AUTOCOMMIT")
    
    async with temp_engine.connect() as conn:
        await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4;"))
    
    await temp_engine.dispose()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mysql_database()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session: 
        await seed_initial_admin(session)

    yield
    await engine.dispose()

app = FastAPI(title="Production Auth API", lifespan=lifespan)

# Register Exception Handlers
app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler) # type: ignore[arg-type]
app.add_exception_handler(InvalidPasswordException, username_password_invalicd_handler) # type: ignore
# Include Central Router
app.include_router(api_router,prefix="/api/v1")