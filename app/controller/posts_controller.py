from fastapi import APIRouter, Form,status
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
# from services.post_service import PostService
# from models import UserModel
from app.core.db import AsyncSessionLocal, get_db_session
from app.core.dependecies import get_current_user
from app.model.user_model import UserModel
from app.repository.posts_repository import PostRepository
from app.schemas.posts_schema import PostCreate, PostResponse
from app.service.posts_service import PostService


router = APIRouter(prefix="/posts",tags=["Posts"])

@router.post("/create-posts", response_model=PostResponse)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSessionLocal = Depends(get_db_session)   # type: ignore
):
    # E podi function eka nathi nisa, Router eka ATHULE mewa ekata amunanna wenawa:
    repo = PostRepository(session)
    service = PostService(repo)

    dto = PostCreate(title=title, content=content)
    post = await service.create_post(dto=dto, user_id=current_user.id, image=image) # type: ignore
    return PostResponse.model_validate(post)


@router.get("/h1")
async def user_profile():
    return {
        "message": "Welcome User! Only USER can access this.",
        "user_data": "current_user"
    }
