from fastapi import APIRouter
from app.controller import ai_controller, oauth, posts_controller, user_controller

api_router = APIRouter();

api_router.include_router(user_controller.router)
api_router.include_router(posts_controller.router)
api_router.include_router(oauth.router)
api_router.include_router(ai_controller.router)