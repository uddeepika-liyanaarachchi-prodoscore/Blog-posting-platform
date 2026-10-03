from fastapi import APIRouter, Form
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.core.db import AsyncSessionLocal, get_db_session
from app.core.dependecies import get_current_user
from app.middleware.roles import authorize_roles
from app.model.posts_model import PostStatus
from app.model.user_model import Role, UserModel
from app.repository.posts_repository import PostRepository
from app.schemas.posts_schema import PostCreate, PostResponse, PostStatusEnum, PostUpdateSchema
from app.service.posts_service import PostService
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/posts",tags=["Posts"])

def get_posts_service(session:AsyncSession=Depends(get_db_session)) -> PostService:
    repo = PostRepository(session)
    return PostService(repo)

@router.post("/create-posts", response_model=PostResponse)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSessionLocal = Depends(get_db_session)   # type: ignore
):
    repo = PostRepository(session)
    service = PostService(repo)

    dto = PostCreate(title=title, content=content)
    post = await service.create_post(dto=dto, user_id=current_user.id, image=image) # type: ignore
    return PostResponse.model_validate(post)

@router.put("/update-posts/{posts_id}",response_model=PostResponse)
async def update_post(
    posts_id: int,
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None), # type: ignore
    service:PostService=Depends(get_posts_service),
    protect: dict=Depends(authorize_roles([Role.USER]))
):
    dto = PostUpdateSchema(
        title=title,
        content=content,
    )
    posts= await service.update_post(posts_id,dto,image=image)
    return PostResponse.model_validate(posts)

@router.patch("/unpublish/{posts_id}",response_model=PostResponse)
async def unpublish_post(posts_id:int,status=PostStatus,service:PostService=Depends(get_posts_service),Depends=(authorize_roles([Role.USER]))):
    posts = await service.unpublish_post(posts_id,status) # type: ignore
    return PostResponse.model_validate(posts)
    
@router.get("/h1")
async def user_profile():
    return {
        "message": "Welcome User! Only USER can access this.",
        "user_data": "current_user"
    }
