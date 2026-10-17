from fastapi import APIRouter, Form, Query
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.core.db import AsyncSessionLocal, get_db_session
from app.core.dependecies import get_current_user
from app.middleware.roles import authorize_roles
from app.model.user_model import Role, UserModel
from app.repository.posts_repository import PostRepository
from app.schemas.posts_schema import PostCreate, PostResponse, PostUpdateSchema
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
    """
    Create a new post for the currently authenticated user.

    - **title**: Title of the post (form data)
    - **content**: Main body/content of the post
    - **image**: Optional image upload (multipart/form-data)
    """

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
    """
    Update post details including title, content, or replace the image.

    - **posts_id**: Target post's unique identifier
    - **title**: Updated title
    - **content**: Updated content
    - **image**: Optional new image replacement
    """
    dto = PostUpdateSchema(
        title=title,
        content=content,
    )
    posts= await service.update_post(posts_id,dto,image=image)
    return PostResponse.model_validate(posts)

@router.patch("/unpublish/{posts_id}",response_model=PostResponse)
async def unpublish_post(posts_id:int,service:PostService=Depends(get_posts_service),Depends=(authorize_roles([Role.USER]))):
    """
    Hide or unpublish a post from public feeds without permanently deleting it.

    - **posts_id**: Unique ID of the post to unpublish
    """
    posts = await service.unpublish_post(posts_id) # type: ignore
    return PostResponse.model_validate(posts)

@router.patch("/delete/{posts_id}",response_model=PostResponse)
async def delete_post(posts_id:int,service:PostService=Depends(get_posts_service),Depends=(authorize_roles([Role.USER]))):
    """
    Soft-delete a post by its ID.

    - **posts_id**: Unique ID of the post to delete
    """
    posts = await service.delete_post(posts_id) # type: ignore
    return PostResponse.model_validate(posts)
   
@router.get("/get-all/{user_id}",response_model=List[PostResponse])
async def load_posts_by_id(
    search: Optional[str] = Query(None, description="Search by title or content"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(authorize_roles([Role.USER])),
    service: PostService = Depends(get_posts_service)
):
    """
    Retrieve a paginated list of posts belonging to the authenticated user.

    Supports optional keyword search filtering by title or content.
    """
    user_id = int(current_user["user_id"])
    offset = (page - 1) * limit
    posts = await service.get_posts(user_id,query=search, limit=limit, offset=offset) 
    return posts 
    

@router.get("/get-all-posts",response_model=List[PostResponse])
async def load_all_posts(
    search: Optional[str] = Query(None, description="Search by title or content"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: PostService = Depends(get_posts_service)
):  
    """
    Retrieve all published posts across all users with pagination and optional search.
    """
    offset = (page - 1) * limit
    posts = await service.get_all_posts(query=search, limit=limit, offset=offset) 
    return posts 
        
    