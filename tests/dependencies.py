import pytest
import jwt
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.dependecies import get_current_user
from app.exceptions_handling.exceptions import InvalidCredentialsException
from app.model.posts_model import Posts_Model
from app.model.user_model import UserModel

@pytest.mark.asyncio
async def test_get_current_user_success(mock_async_session):
   fake_token = "valid_access_token"
   expected_user = UserModel(id=1, email="test@example.com", role="user")


   mock_result = MagicMock()
   mock_result.scalar_one_or_none.return_value = expected_user
   mock_async_session.execute.return_value = mock_result


   with patch("app.core.dependecies.decode_access_token") as mock_decode:
       mock_decode.return_value = {"sub": "test@example.com", "user_id": 1, "type": "access"}
      
       user = await get_current_user(token=fake_token, db=mock_async_session)
       assert user == expected_user
       assert user.id == 1 # type: ignore
       assert user.email == "test@example.com" # type: ignore


@pytest.mark.asyncio
async def test_get_current_user_missing_user_id(mock_async_session):
   fake_token = "valid_access_token"


   with patch("app.core.dependecies.decode_access_token") as mock_decode:
       mock_decode.return_value = {"sub": "test@example.com", "type": "access"}
      
       with pytest.raises(InvalidCredentialsException, match="Invalid token or session expired"):
           await get_current_user(token=fake_token, db=mock_async_session)


@pytest.mark.asyncio
async def test_get_current_user_jwt_error(mock_async_session):
   fake_token = "invalid_token"


   with patch("app.core.dependecies.decode_access_token", side_effect=jwt.PyJWTError("Token decode failed")):
       with pytest.raises(InvalidCredentialsException, match="JWT Invalid token or session expired"):
           await get_current_user(token=fake_token, db=mock_async_session)


@pytest.mark.asyncio
async def test_get_current_user_not_found_in_db(mock_async_session):
   fake_token = "valid_access_token"


   mock_result = MagicMock()
   mock_result.scalar_one_or_none.return_value = None
   mock_async_session.execute.return_value = mock_result


   with patch("app.core.dependecies.decode_access_token") as mock_decode:
       mock_decode.return_value = {"sub": "nonexistent@example.com", "user_id": 99, "type": "access"}
      
       with pytest.raises(InvalidCredentialsException, match="Invalid User"):
           await get_current_user(token=fake_token, db=mock_async_session)


