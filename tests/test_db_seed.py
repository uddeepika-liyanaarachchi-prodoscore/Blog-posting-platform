import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.db import get_db_session
from app.core.seed import seed_initial_admin
from app.model.user_model import Role, UserModel
from app.model.posts_model import Posts_Model

@pytest.mark.asyncio
async def test_get_db_session():
   mock_session = AsyncMock()
   mock_session.close = AsyncMock()


   with patch("app.core.db.AsyncSessionLocal") as mock_session_local:
       mock_session_local.return_value.__aenter__.return_value = mock_session
       mock_session_local.return_value.__aexit__.return_value = None


       gen = get_db_session()
       session = await anext(gen)
       assert session == mock_session


       with pytest.raises(StopAsyncIteration):
           await anext(gen)


@pytest.mark.asyncio
async def test_seed_initial_admin_when_not_exists(mock_async_session):
   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.first.return_value = None
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   with patch.dict("os.environ", {"FIRST_ADMIN_EMAIL": "superadmin@example.com", "FIRST_ADMIN_PASSWORD": "admin_secret"}):
       await seed_initial_admin(mock_async_session)


   assert mock_async_session.add.called
   assert mock_async_session.commit.called
   added_user = mock_async_session.add.call_args[0][0]
   assert isinstance(added_user, UserModel)
   assert added_user.email == "superadmin@example.com" # type: ignore
   assert added_user.role == Role.ADMIN.value # type: ignore


@pytest.mark.asyncio
async def test_seed_initial_admin_when_already_exists(mock_async_session):
   existing_admin = UserModel(id=1, email="admin@example.com", role=Role.ADMIN.value)
   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.first.return_value = existing_admin
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   await seed_initial_admin(mock_async_session)


   mock_async_session.add.assert_not_called()
   mock_async_session.commit.assert_not_called()



