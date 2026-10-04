import pytest
import jwt
from datetime import datetime, timezone, timedelta
from app.core.security import (
   hash_password,
   verify_password,
   create_access_token,
   create_refresh_token,
   decode_access_token,
   decode_refresh_token,
)
from app.core.config import settings


def test_hash_password():
   password = "secret_password123"
   hashed = hash_password(password)
   assert hashed != password
   assert isinstance(hashed, str)
   assert len(hashed) > 0


def test_verify_password_success():
   password = "secret_password123"
   hashed = hash_password(password)
   assert verify_password(password, hashed) is True


def test_verify_password_failure():
   password = "secret_password123"
   wrong_password = "wrong_password"
   hashed = hash_password(password)
   assert verify_password(wrong_password, hashed) is False


def test_create_and_decode_access_token():
   payload = {"sub": "user@example.com", "user_id": 1, "role": "user"}
   token = create_access_token(payload)
   assert isinstance(token, str)
  
   decoded = decode_access_token(token)
   assert decoded["sub"] == "user@example.com"
   assert decoded["user_id"] == 1
   assert decoded["role"] == "user"
   assert decoded["type"] == "access"
   assert "exp" in decoded


def test_create_and_decode_refresh_token():
   payload = {"sub": "user@example.com", "user_id": 1, "role": "user"}
   token = create_refresh_token(payload)
   assert isinstance(token, str)
  
   decoded = decode_refresh_token(token)
   assert decoded["sub"] == "user@example.com"
   assert decoded["user_id"] == 1
   assert decoded["role"] == "user"
   assert decoded["type"] == "refresh"
   assert "exp" in decoded


def test_decode_access_token_invalid_signature():
   payload = {"sub": "user@example.com", "user_id": 1, "role": "user", "type": "access"}
   fake_token = jwt.encode(payload, "different_secret_key_that_is_long_enough_32_bytes", algorithm="HS256")
  
   with pytest.raises(jwt.PyJWTError):
       decode_access_token(fake_token)


def test_decode_refresh_token_invalid_signature():
   payload = {"sub": "user@example.com", "user_id": 1, "role": "user", "type": "refresh"}
   fake_token = jwt.encode(payload, "different_secret_key_that_is_long_enough_32_bytes", algorithm="HS256")
  
   with pytest.raises(jwt.PyJWTError):
       decode_refresh_token(fake_token)


import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
from main import init_mysql_database, lifespan, app_exception_handler, app
from app.exceptions_handling.exceptions import UserAlreadyExistsException, PostsNotFoundException


@pytest.mark.asyncio
async def test_init_mysql_database():
   mock_engine = MagicMock()
   mock_conn = AsyncMock()
   mock_engine.connect.return_value.__aenter__.return_value = mock_conn
   mock_engine.connect.return_value.__aexit__.return_value = None
   mock_engine.dispose = AsyncMock()


   with patch("main.create_async_engine", return_value=mock_engine) as mock_create_engine:
       await init_mysql_database()
       mock_create_engine.assert_called_once()
       mock_conn.execute.assert_called_once()
       mock_engine.dispose.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan():
   mock_engine = MagicMock()
   mock_conn = AsyncMock()
   mock_conn.run_sync = AsyncMock()
   mock_engine.begin.return_value.__aenter__.return_value = mock_conn
   mock_engine.begin.return_value.__aexit__.return_value = None
   mock_engine.dispose = AsyncMock()


   mock_session = AsyncMock()
   mock_session_local = MagicMock()
   mock_session_local.return_value.__aenter__.return_value = mock_session
   mock_session_local.return_value.__aexit__.return_value = None


   with patch("main.init_mysql_database", new_callable=AsyncMock) as mock_init_db, \
        patch("main.engine", mock_engine), \
        patch("main.AsyncSessionLocal", mock_session_local), \
        patch("main.seed_initial_admin", new_callable=AsyncMock) as mock_seed:


       async with lifespan(app):
           mock_init_db.assert_called_once()
           mock_conn.run_sync.assert_called_once()
           mock_seed.assert_called_once_with(mock_session)


       mock_engine.dispose.assert_called_once()


@pytest.mark.asyncio
async def test_app_exception_handler():
   mock_request = MagicMock(spec=Request)
   exc = UserAlreadyExistsException(email="duplicate@example.com")


   response = await app_exception_handler(mock_request, exc)
   assert response.status_code == 409
  
   import json
   body = json.loads(response.body.decode()) # type: ignore
   assert body["success"] is False
   assert body["error_code"] == "UserAlreadyExistsException"
   assert "duplicate@example.com" in body["message"]


@pytest.mark.asyncio
async def test_app_exception_handler_posts():
   mock_request = MagicMock(spec=Request)
   exc = PostsNotFoundException(identifier=42)


   response = await app_exception_handler(mock_request, exc)
   assert response.status_code == 404
  
   import json
   body = json.loads(response.body.decode()) # type: ignore
   assert body["success"] is False
   assert body["error_code"] == "PostsNotFoundException"
   assert "42" in body["message"]
