import pytest
import jwt
from fastapi import HTTPException, status
from app.middleware.auth import authenticate
from app.middleware.roles import authorize_roles
from app.model.user_model import Role
from unittest.mock import patch


@pytest.mark.asyncio
async def test_authenticate_missing_header():
   with pytest.raises(HTTPException) as exc_info:
       await authenticate(authorization=None) # type: ignore
   assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
   assert "Authorization header missing" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authenticate_invalid_format():
   with pytest.raises(HTTPException) as exc_info:
       await authenticate(authorization="Token123")
   assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


   with pytest.raises(HTTPException) as exc_info:
       await authenticate(authorization="Basic dXNlcjpwYXNz")
   assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_authenticate_wrong_token_type():
   with patch("app.middleware.auth.decode_access_token") as mock_decode:
       mock_decode.return_value = {"type": "refresh", "sub": "test@example.com"}
       with pytest.raises(HTTPException) as exc_info:
           await authenticate(authorization="Bearer some_token")
       assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
       assert "Must be an access token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authenticate_expired_token():
   with patch("app.middleware.auth.decode_access_token", side_effect=jwt.ExpiredSignatureError):
       with pytest.raises(HTTPException) as exc_info:
           await authenticate(authorization="Bearer expired_token")
       assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
       assert "Access token expired" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authenticate_invalid_token():
   with patch("app.middleware.auth.decode_access_token", side_effect=jwt.PyJWTError):
       with pytest.raises(HTTPException) as exc_info:
           await authenticate(authorization="Bearer invalid_token")
       assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
       assert "Invalid token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authenticate_success():
   expected_payload = {"type": "access", "sub": "test@example.com", "user_id": 1, "role": "user"}
   with patch("app.middleware.auth.decode_access_token", return_value=expected_payload):
       payload = await authenticate(authorization="Bearer valid_token")
       assert payload == expected_payload


@pytest.mark.asyncio
async def test_authorize_roles_success():
   role_checker = authorize_roles([Role.ADMIN, Role.USER])
   current_user = {"user_id": 1, "role": "admin"}
  
   result = await role_checker(current_user=current_user)
   assert result == current_user


@pytest.mark.asyncio
async def test_authorize_roles_forbidden():
   role_checker = authorize_roles([Role.ADMIN])
   current_user = {"user_id": 1, "role": "user"}
  
   with pytest.raises(HTTPException) as exc_info:
       await role_checker(current_user=current_user)
   assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
   assert "Forbidden" in exc_info.value.detail



