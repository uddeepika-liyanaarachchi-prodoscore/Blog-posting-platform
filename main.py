from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers.router import api_router
from app.core.db import AsyncSessionLocal, engine, Base
from app.core.seed import seed_initial_admin
from fastapi import FastAPI , Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi.responses import JSONResponse
from app.exceptions_handling.exceptions import AppExceptions
from fastapi.middleware.cors import CORSMiddleware  

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
origins = [
    "http://localhost:5500",      
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,           
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Requested-With",
    ],                               
)

@app.exception_handler(AppExceptions)
async def app_exception_handler(request: Request, exc: AppExceptions):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.__class__.__name__,
            "message": exc.message
        }
    )
# Include Central Router
app.include_router(api_router,prefix="/api/v1")