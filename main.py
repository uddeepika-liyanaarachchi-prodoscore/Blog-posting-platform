from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers.router import api_router
from app.core.db import AsyncSessionLocal, engine, Base
from app.core.seed import seed_initial_admin
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions_handling.exceptions import AppExceptions
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session: 
        await seed_initial_admin(session)

    yield
    await engine.dispose()

app = FastAPI(title="Production Auth API", lifespan=lifespan)

origins = [
    "http://localhost:5500",      
    "http://127.0.0.1:5501",
    "http://127.0.0.1:3000",
    "https://uddeepika-liyanaarachchi-prodoscore.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,           
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
    allow_headers=[
        "Content-Type",
        "Authorization",
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
app.include_router(api_router, prefix="/api/v1")