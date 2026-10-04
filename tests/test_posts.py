import pytest
from unittest.mock import AsyncMock, MagicMock , patch
from io import BytesIO
from fastapi import UploadFile
from app.controller.posts_controller import (
   get_posts_service,
   create_post,
   update_post,
   unpublish_post,
   delete_post,
   load_posts_by_id,
   load_all_posts,
)
from app.model.posts_model import Posts_Model, PostStatus
from app.model.user_model import UserModel, Role
from app.schemas.posts_schema import PostResponse, PostStatusEnum
from app.repository.posts_repository import PostRepository
from app.service.posts_service import PostService
from app.schemas.posts_schema import PostCreate, PostUpdateSchema
from app.exceptions_handling.exceptions import PostsNotFoundException
from pydantic import ConfigDict

# controller layer unit tests 

def test_get_posts_service(mock_async_session):
   service = get_posts_service(mock_async_session)
   assert service is not None
   assert service._post_repository is not None


@pytest.mark.asyncio
async def test_controller_create_post(mock_async_session):
   dummy_user = UserModel(id=1, email="test@example.com", role=Role.USER.value)
   fake_file = UploadFile(filename="pic.jpg", file=BytesIO(b"data"))
  
   created_model = Posts_Model(
       id=10,
       title="My First Post",
       content="Post content",
       image_url="http://img.png",
       status=PostStatus.PUBLISHED,
       user_id=1
   )


   with pytest.MonkeyPatch.context() as mp:
       mock_service = MagicMock()
       mock_service.create_post = AsyncMock(return_value=created_model)
       mp.setattr("app.controller.posts_controller.PostService", lambda repo: mock_service)


       res = await create_post(
           title="My First Post",
           content="Post content",
           image=fake_file,
           current_user=dummy_user,
           session=mock_async_session
       )


       assert res.id == 10
       assert res.title == "My First Post"
       assert res.content == "Post content"
       assert res.image_url == "http://img.png"
       assert res.status == PostStatusEnum.PUBLISHED
       assert res.user_id == 1


@pytest.mark.asyncio
async def test_controller_update_post():
   mock_service = MagicMock()
   mock_service.update_post = AsyncMock()
   updated_post = Posts_Model(
       id=10,
       title="Updated Title",
       content="Updated Content",
       image_url=None,
       status=PostStatus.UNPUBLISHED,
       user_id=1
   )
   mock_service.update_post.return_value = updated_post


   res = await update_post(
       posts_id=10,
       title="Updated Title",
       content="Updated Content",
       image=None,
       service=mock_service,
       protect={"user_id": 1, "role": "user"}
   )


   assert res.id == 10
   assert res.title == "Updated Title"
   assert res.content == "Updated Content"
   mock_service.update_post.assert_called_once()


@pytest.mark.asyncio
async def test_controller_unpublish_post():
   mock_service = MagicMock()
   mock_service.unpublish_post = AsyncMock()
   post = Posts_Model(
       id=10,
       title="Title",
       content="Content",
       image_url=None,
       status=PostStatus.UNPUBLISHED,
       user_id=1
   )
   mock_service.unpublish_post.return_value = post


   res = await unpublish_post(posts_id=10, service=mock_service)
   assert res.id == 10
   assert res.status == PostStatusEnum.UNPUBLISHED
   mock_service.unpublish_post.assert_called_once_with(10)


@pytest.mark.asyncio
async def test_controller_delete_post():
   mock_service = MagicMock()
   mock_service.delete_post = AsyncMock()
   post = Posts_Model(
       id=10,
       title="Title",
       content="Content",
       image_url=None,
       status=PostStatus.DELETED,
       user_id=1
   )
   mock_service.delete_post.return_value = post


   res = await delete_post(posts_id=10, service=mock_service)
   assert res.id == 10
   assert res.status == PostStatusEnum.DELETED
   mock_service.delete_post.assert_called_once_with(10)


@pytest.mark.asyncio
async def test_controller_load_posts_by_id():
   mock_service = MagicMock()
   mock_service.get_posts = AsyncMock()
   posts = [
       Posts_Model(id=1, title="T1", content="C1", image_url=None, status=PostStatus.PUBLISHED, user_id=2),
       Posts_Model(id=2, title="T2", content="C2", image_url=None, status=PostStatus.PUBLISHED, user_id=2),
   ]
   mock_service.get_posts.return_value = posts


   current_user = {"user_id": 2, "role": "user"}
   res = await load_posts_by_id(current_user=current_user, service=mock_service)


   assert len(res) == 2
   mock_service.get_posts.assert_called_once_with(2)


@pytest.mark.asyncio
async def test_controller_load_all_posts():
   mock_service = MagicMock()
   mock_service.get_all_posts = AsyncMock()
   posts = [
       Posts_Model(id=1, title="T1", content="C1", image_url=None, status=PostStatus.PUBLISHED, user_id=1),
   ]
   mock_service.get_all_posts.return_value = posts


   current_user = {"user_id": 1, "role": "user"}
   res = await load_all_posts(current_user=current_user, service=mock_service)


   assert len(res) == 1
   mock_service.get_all_posts.assert_called_once()




# Repository layer unit testing for posts

@pytest.mark.asyncio
async def test_post_repo_create(mock_async_session):
   repo = PostRepository(mock_async_session)
   post = Posts_Model(title="Test Title", content="Test Content", user_id=1, status=PostStatus.PUBLISHED.value)


   created = await repo.create(post)
   assert created == post
   mock_async_session.add.assert_called_once_with(post)
   mock_async_session.commit.assert_called_once()
   mock_async_session.refresh.assert_called_once_with(post)


@pytest.mark.asyncio
async def test_post_repo_get_by_id(mock_async_session):
   repo = PostRepository(mock_async_session)
   post = Posts_Model(id=1, title="Test", content="Body", user_id=1)


   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.first.return_value = post
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   result = await repo.get_by_id(1)
   assert result == post
   assert result.id == 1 # type: ignore


@pytest.mark.asyncio
async def test_post_repo_get_posts_by_user_id(mock_async_session):
   repo = PostRepository(mock_async_session)
   posts = [
       Posts_Model(id=1, title="Post 1", content="Body 1", user_id=2),
       Posts_Model(id=2, title="Post 2", content="Body 2", user_id=2),
   ]


   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.all.return_value = posts
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   result = await repo.get_posts_by_user_id(2)
   assert len(result) == 2
   assert result == posts


@pytest.mark.asyncio
async def test_post_repo_update(mock_async_session):
   repo = PostRepository(mock_async_session)
   post = Posts_Model(id=1, title="Updated Title", content="Updated Content", user_id=1)


   updated = await repo.update(post)
   assert updated == post
   mock_async_session.add.assert_called_once_with(post)
   mock_async_session.commit.assert_called_once()
   mock_async_session.refresh.assert_called_once_with(post)


@pytest.mark.asyncio
async def test_post_repo_delete(mock_async_session):
   repo = PostRepository(mock_async_session)
   post = Posts_Model(id=1, title="Title", content="Content", user_id=1, status=PostStatus.DELETED.value)


   deleted = await repo.delete(post)
   assert deleted == post
   mock_async_session.add.assert_called_once_with(post)
   mock_async_session.commit.assert_called_once()
   mock_async_session.refresh.assert_called_once_with(post)


@pytest.mark.asyncio
async def test_post_repo_update_status(mock_async_session):
   repo = PostRepository(mock_async_session)
   post = Posts_Model(id=1, title="Title", content="Content", user_id=1, status=PostStatus.UNPUBLISHED.value)


   updated = await repo.update_status(post)
   assert updated == post
   mock_async_session.add.assert_called_once_with(post)
   mock_async_session.commit.assert_called_once()
   mock_async_session.refresh.assert_called_once_with(post)


@pytest.mark.asyncio
async def test_post_repo_get_all_published(mock_async_session):
   repo = PostRepository(mock_async_session)
   published_posts = [
       Posts_Model(id=2, title="Post 2", content="Content 2", status=PostStatus.PUBLISHED.value, user_id=1),
       Posts_Model(id=1, title="Post 1", content="Content 1", status=PostStatus.PUBLISHED.value, user_id=2),
   ]


   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.all.return_value = published_posts
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   result = await repo.get_all_published()
   assert len(result) == 2
   assert result == published_posts

# Service layer unit tests for posts 

@pytest.fixture
def mock_post_repo():
   repo = MagicMock()
   repo.create = AsyncMock()
   repo.get_by_id = AsyncMock()
   repo.get_posts_by_user_id = AsyncMock()
   repo.update = AsyncMock()
   repo.delete = AsyncMock()
   repo.update_status = AsyncMock()
   repo.get_all_published = AsyncMock()
   return repo


@pytest.fixture
def post_service(mock_post_repo):
   return PostService(mock_post_repo)


@pytest.mark.asyncio
async def test_create_post_without_image(post_service, mock_post_repo):
   created_post = Posts_Model(id=1, title="Hello", content="World", user_id=1, image_url=None, status=PostStatus.PUBLISHED.value)
   mock_post_repo.create.return_value = created_post


   dto = PostCreate(title="Hello", content="World")
   result = await post_service.create_post(dto=dto, user_id=1, image=None)


   assert result == created_post
   mock_post_repo.create.assert_called_once()
   saved = mock_post_repo.create.call_args[0][0]
   assert saved.title == "Hello"
   assert saved.image_url is None


@pytest.mark.asyncio
async def test_create_post_with_image(post_service, mock_post_repo):
   created_post = Posts_Model(id=1, title="Hello", content="World", user_id=1, image_url="http://img.png", status=PostStatus.PUBLISHED.value)
   mock_post_repo.create.return_value = created_post


   fake_file = UploadFile(filename="test.png", file=BytesIO(b"img"))
   dto = PostCreate(title="Hello", content="World")


   with patch("app.service.posts_service.upload_image_to_cloudinary", return_value="http://img.png") as mock_upload:
       result = await post_service.create_post(dto=dto, user_id=1, image=fake_file)
       assert result == created_post
       mock_upload.assert_called_once_with(fake_file)


@pytest.mark.asyncio
async def test_update_post_success(post_service, mock_post_repo):
   existing_post = Posts_Model(id=1, title="Old", content="Old Content", status=PostStatus.UNPUBLISHED)
   mock_post_repo.get_by_id.return_value = existing_post
   mock_post_repo.update.return_value = existing_post


   dto = PostUpdateSchema(title="New", content="New Content")
   result = await post_service.update_post(1, dto)


   assert result == existing_post
   mock_post_repo.update.assert_called_once_with(existing_post)


@pytest.mark.asyncio
async def test_update_post_not_unpublished_raises(post_service, mock_post_repo):
   existing_post = Posts_Model(id=1, title="Old", content="Old Content", status=PostStatus.PUBLISHED)
   mock_post_repo.get_by_id.return_value = existing_post


   dto = PostUpdateSchema(title="New", content="New Content")
   with pytest.raises(PostsNotFoundException):
       await post_service.update_post(1, dto)


@pytest.mark.asyncio
async def test_unpublish_post_from_published(post_service, mock_post_repo):
   existing_post = Posts_Model(id=1, title="Title", content="Content", status=PostStatus.PUBLISHED)
   mock_post_repo.get_by_id.return_value = existing_post
   mock_post_repo.update.return_value = existing_post


   result = await post_service.unpublish_post(1)
   assert existing_post.status == PostStatus.UNPUBLISHED # type: ignore
   mock_post_repo.update.assert_called_once_with(existing_post)


@pytest.mark.asyncio
async def test_unpublish_post_from_unpublished(post_service, mock_post_repo):
   existing_post = Posts_Model(id=1, title="Title", content="Content", status=PostStatus.UNPUBLISHED)
   mock_post_repo.get_by_id.return_value = existing_post
   mock_post_repo.update_status.return_value = existing_post


   result = await post_service.unpublish_post(1)
   assert existing_post.status == PostStatus.PUBLISHED # type: ignore
   mock_post_repo.update_status.assert_called_once_with(existing_post)


@pytest.mark.asyncio
async def test_unpublish_post_invalid_status(post_service, mock_post_repo):
   existing_post = Posts_Model(id=1, title="Title", content="Content", status=PostStatus.DELETED)
   mock_post_repo.get_by_id.return_value = existing_post


   with pytest.raises(PostsNotFoundException):
       await post_service.unpublish_post(1)


@pytest.mark.asyncio
async def test_delete_post_success(post_service, mock_post_repo):
   existing_post = Posts_Model(id=1, title="Title", content="Content", status=PostStatus.UNPUBLISHED)
   mock_post_repo.get_by_id.return_value = existing_post
   mock_post_repo.delete.return_value = existing_post


   result = await post_service.delete_post(1)
   assert existing_post.status == PostStatus.DELETED # type: ignore
   mock_post_repo.delete.assert_called_once_with(existing_post)


@pytest.mark.asyncio
async def test_delete_post_not_unpublished_raises(post_service, mock_post_repo):
   existing_post = Posts_Model(id=1, title="Title", content="Content", status=PostStatus.PUBLISHED)
   mock_post_repo.get_by_id.return_value = existing_post


   with pytest.raises(PostsNotFoundException):
       await post_service.delete_post(1)


@pytest.mark.asyncio
async def test_get_posts(post_service, mock_post_repo):
   posts = [Posts_Model(id=1, title="P1", content="C1", user_id=10)]
   mock_post_repo.get_posts_by_user_id.return_value = posts


   res = await post_service.get_posts(10)
   assert res == posts
   mock_post_repo.get_posts_by_user_id.assert_called_once_with(10)


@pytest.mark.asyncio
async def test_get_all_posts(post_service, mock_post_repo):
   posts = [Posts_Model(id=1, title="P1", content="C1", status=PostStatus.PUBLISHED.value)]
   mock_post_repo.get_all_published.return_value = posts


   res = await post_service.get_all_posts()
   assert res == posts
   mock_post_repo.get_all_published.assert_called_once()


