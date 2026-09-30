

from contextlib import asynccontextmanager
from app.core.exceptions import InvalidPasswordException, UserAlreadyExistsException, user_already_exists_handler ,username_password_invalicd_handler
from app.routers.user_router import router as user_router
from app.core.db import engine, Base
from fastapi import FastAPI


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
app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler) # type: ignore[arg-type]
app.add_exception_handler(InvalidPasswordException, username_password_invalicd_handler) # type: ignore
# Include Central Router
app.include_router(user_router,prefix="/api/v1")