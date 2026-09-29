from fastapi import FastAPI
from contextlib import asynccontextmanager

# from core.exceptions import (
#     UserAlreadyExistsException, user_already_exists_handler,
#     InvalidCredentialsException, invalid_credentials_handler
# )
from app.core.db import Base
from app.core.db import engine
# from routers.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup: Create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # App shutdown
    await engine.dispose()

app = FastAPI(title="Production Auth API", lifespan=lifespan)

# Register Exception Handlers
# app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler)
# app.add_exception_handler(InvalidCredentialsException, invalid_credentials_handler)

# Include Central Router
# app.include_router(api_router)