import pytest
from unittest.mock import AsyncMock, MagicMock , patch
from fastapi import BackgroundTasks
import jwt
from datetime import datetime, timezone, timedelta
from fastapi import BackgroundTasks, HTTPException, status
from app.model.posts_model import Posts_Model
from app.service.user_service import AuthService
from app.model.password_reset_model import PasswordResetModel
from app.core.security import hash_password

from app.controller.user_controller import (
   get_auth_service,
   register,
   register_admin,
   login,
   refresh_token,
   get_my_profile,
   update_my_profile,
   forgot_password,
   reset_password,
)
from app.model.user_model import UserModel, Role
from app.schemas.user_schema import (
   UserRegisterSchema,
   UserLoginSchema,
   RefreshTokenRequestSchema,
   UserProfileUpdateSchema,
   ForgotPasswordRequestSchema,
   ResetPasswordRequestSchema,
   UserResponseSchema,
   TokenResponseSchema,
)
from app.exceptions_handling.exceptions import (
   UserAlreadyExistsException,
   UserNotFoundException,
   InvalidCredentialsException,
)

# Unit Tests for USER Controller 

def test_get_auth_service(mock_async_session):
   service = get_auth_service(mock_async_session)
   assert service is not None
   assert service._user_repository is not None


@pytest.mark.asyncio
async def test_controller_register():
   mock_service = MagicMock()
   mock_service.register = AsyncMock()
   fake_user = UserModel(id=1, email="test@example.com", role=Role.USER.value)
   mock_service.register.return_value = fake_user

   body = UserRegisterSchema(email="test@example.com", password="password123")
   res = await register(body=body, service=mock_service)
  
   assert res.email == "test@example.com"
   assert res.id == 1
   mock_service.register.assert_called_once_with(body)


@pytest.mark.asyncio
async def test_controller_register_admin():
   mock_service = MagicMock()
   mock_service.register_admin = AsyncMock()
   fake_admin = UserModel(id=2, email="admin@example.com", role=Role.ADMIN.value)
   mock_service.register_admin.return_value = fake_admin


   body = UserRegisterSchema(email="admin@example.com", password="adminpassword")
   current_user = {"user_id": 1, "role": "admin"}
   res = await register_admin(body=body, service=mock_service, current_user=current_user)


   assert res.email == "admin@example.com"
   assert res.role == Role.ADMIN
   mock_service.register_admin.assert_called_once_with(body)


@pytest.mark.asyncio
async def test_controller_login():
   mock_service = MagicMock()
   mock_service.login = AsyncMock()
   mock_service.login.return_value = {
       "access_token": "acc",
       "refresh_token": "ref",
       "role": Role.USER.value,
       "token_type": "bearer"
   }

   body = UserLoginSchema(email="test@example.com", password="password")
   res = await login(body=body, service=mock_service)

   assert res.access_token == "acc"
   assert res.refresh_token == "ref"
   assert res.role == Role.USER
   mock_service.login.assert_called_once_with(body)

@pytest.mark.asyncio
async def test_controller_refresh_token():
   mock_service = MagicMock()
   mock_service.refresh_access_token = AsyncMock()
   mock_service.refresh_access_token.return_value = {
       "access_token": "new_acc",
       "refresh_token": "existing_ref",
       "role": Role.USER.value,
       "token_type": "bearer"
   }


   body = RefreshTokenRequestSchema(refresh_token="existing_ref")
   res = await refresh_token(body=body, service=mock_service)


   assert res.access_token == "new_acc"
   assert res.refresh_token == "existing_ref"
   mock_service.refresh_access_token.assert_called_once_with("existing_ref")


@pytest.mark.asyncio
async def test_controller_get_my_profile():
   mock_service = MagicMock()
   mock_service.get_profile = AsyncMock()
   user = UserModel(id=1, email="test@example.com", role=Role.USER.value)
   mock_service.get_profile.return_value = user


   current_user = {"user_id": 1, "role": "user"}
   res = await get_my_profile(current_user=current_user, service=mock_service)


   assert res == user
   mock_service.get_profile.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_controller_update_my_profile():
   mock_service = MagicMock()
   mock_service.update_profile = AsyncMock()
   updated_user = UserModel(id=1, email="test@example.com", first_name="John", role=Role.USER.value)
   mock_service.update_profile.return_value = updated_user


   body = UserProfileUpdateSchema(first_name="John")
   current_user = {"user_id": 1, "role": "user"}
   res = await update_my_profile(body=body, current_user=current_user, service=mock_service)


   assert res == updated_user
   mock_service.update_profile.assert_called_once_with(1, body)


@pytest.mark.asyncio
async def test_controller_forgot_password():
   mock_service = MagicMock()
   mock_service.request_password_reset = AsyncMock()
   mock_service.request_password_reset.return_value = {"message": "OTP sent"}


   body = ForgotPasswordRequestSchema(email="test@example.com")
   bg_tasks = MagicMock(spec=BackgroundTasks)
   res = await forgot_password(body=body, bg_tasks=bg_tasks, service=mock_service)


   assert res == {"message": "OTP sent"}
   mock_service.request_password_reset.assert_called_once_with(body, bg_tasks)


@pytest.mark.asyncio
async def test_controller_reset_password():
   mock_service = MagicMock()
   mock_service.reset_password = AsyncMock()
   mock_service.reset_password.return_value = {"message": "Password reset successfully"}


   body = ResetPasswordRequestSchema(email="test@example.com", otp="123456", new_password="newpass")
   res = await reset_password(body=body, service=mock_service)


   assert res == {"message": "Password reset successfully"}
   mock_service.reset_password.assert_called_once_with(body)

# Unit Tests for User Repository

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from app.repository.user_repository import UserRepository
from app.model.user_model import UserModel, Role
from app.model.password_reset_model import PasswordResetModel


@pytest.mark.asyncio
async def test_user_repo_get_by_email(mock_async_session):
   repo = UserRepository(mock_async_session)
   dummy_user = UserModel(id=1, email="test@example.com", role=Role.USER.value)
  
   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.first.return_value = dummy_user
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   user = await repo.get_by_email("test@example.com")
   assert user == dummy_user
   assert mock_async_session.execute.called


@pytest.mark.asyncio
async def test_user_repo_create(mock_async_session):
   repo = UserRepository(mock_async_session)
   new_user = UserModel(email="new@example.com", hashed_password="hash", role=Role.USER.value)


   user = await repo.create(new_user)
   assert user == new_user
   mock_async_session.add.assert_called_once_with(new_user)
   mock_async_session.commit.assert_called_once()
   mock_async_session.refresh.assert_called_once_with(new_user)


@pytest.mark.asyncio
async def test_user_repo_get_by_id(mock_async_session):
   repo = UserRepository(mock_async_session)
   dummy_user = UserModel(id=5, email="user5@example.com", role=Role.USER.value)


   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.first.return_value = dummy_user
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   user = await repo.get_by_id(5)
   assert user == dummy_user
   assert user.id == 5  # type: ignore


@pytest.mark.asyncio
async def test_user_repo_update(mock_async_session):
   repo = UserRepository(mock_async_session)
   user = UserModel(id=1, email="test@example.com", first_name="John")


   updated = await repo.update(user)
   assert updated == user
   mock_async_session.add.assert_called_once_with(user)
   mock_async_session.commit.assert_called_once()
   mock_async_session.refresh.assert_called_once_with(user)


@pytest.mark.asyncio
async def test_user_repo_save_otp(mock_async_session):
   repo = UserRepository(mock_async_session)
   reset_entry = PasswordResetModel(
       email="test@example.com",
       otp_code="123456",
       expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10),
       is_used=False
   )


   saved = await repo.save_otp(reset_entry)
   assert saved == reset_entry
   mock_async_session.add.assert_called_once_with(reset_entry)
   mock_async_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_user_repo_get_valid_otp(mock_async_session):
   repo = UserRepository(mock_async_session)
   reset_entry = PasswordResetModel(
       email="test@example.com",
       otp_code="123456",
       expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10),
       is_used=False
   )


   mock_result = MagicMock()
   mock_scalars = MagicMock()
   mock_scalars.first.return_value = reset_entry
   mock_result.scalars.return_value = mock_scalars
   mock_async_session.execute.return_value = mock_result


   result = await repo.get_valid_otp("test@example.com", "123456")
   assert result == reset_entry

# Unit tests for User service 

@pytest.fixture
def mock_user_repo():
   repo = MagicMock()
   repo.get_by_email = AsyncMock()
   repo.create = AsyncMock()
   repo.get_by_id = AsyncMock()
   repo.update = AsyncMock()
   repo.save_otp = AsyncMock()
   repo.get_valid_otp = AsyncMock()
   return repo


@pytest.fixture
def auth_service(mock_user_repo):
   return AuthService(mock_user_repo)


@pytest.mark.asyncio
async def test_register_success(auth_service, mock_user_repo):
   mock_user_repo.get_by_email.return_value = None
   created_user = UserModel(id=1, email="test@example.com", hashed_password="hashed_pwd", role=Role.USER.value)
   mock_user_repo.create.return_value = created_user


   dto = UserRegisterSchema(email="test@example.com", password="password123")
   user = await auth_service.register(dto)


   assert user == created_user
   mock_user_repo.create.assert_called_once()
   saved_arg = mock_user_repo.create.call_args[0][0]
   assert saved_arg.email == "test@example.com"
   assert saved_arg.role == Role.USER.value


@pytest.mark.asyncio
async def test_register_already_exists(auth_service, mock_user_repo):
   existing_user = UserModel(id=1, email="test@example.com", role=Role.USER.value)
   mock_user_repo.get_by_email.return_value = existing_user


   dto = UserRegisterSchema(email="test@example.com", password="password123")
   with pytest.raises(UserAlreadyExistsException):
       await auth_service.register(dto)

@pytest.mark.asyncio
async def test_register_admin_success(auth_service, mock_user_repo):
   mock_user_repo.get_by_email.return_value = None
   created_admin = UserModel(id=2, email="admin@example.com", hashed_password="hashed_pwd", role=Role.ADMIN.value)
   mock_user_repo.create.return_value = created_admin

   dto = UserRegisterSchema(email="admin@example.com", password="adminpassword")
   admin = await auth_service.register_admin(dto)

   assert admin == created_admin
   saved_arg = mock_user_repo.create.call_args[0][0]
   assert saved_arg.email == "admin@example.com"
   assert saved_arg.role == Role.ADMIN.value

@pytest.mark.asyncio
async def test_register_admin_already_exists(auth_service, mock_user_repo):
   mock_user_repo.get_by_email.return_value = UserModel(id=1, email="admin@example.com")
   dto = UserRegisterSchema(email="admin@example.com", password="adminpassword")
   with pytest.raises(UserAlreadyExistsException):
       await auth_service.register_admin(dto)


@pytest.mark.asyncio
async def test_login_success(auth_service, mock_user_repo):
   hashed_pwd = hash_password("password123")
   user = UserModel(id=1, email="test@example.com", hashed_password=hashed_pwd, role=Role.USER.value)
   mock_user_repo.get_by_email.return_value = user

   dto = UserLoginSchema(email="test@example.com", password="password123")
   res = await auth_service.login(dto)

   assert "access_token" in res
   assert "refresh_token" in res
   assert res["role"] == Role.USER.value
   assert res["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_user_repo):
   mock_user_repo.get_by_email.return_value = None
   dto = UserLoginSchema(email="notfound@example.com", password="password123")

   with pytest.raises(InvalidCredentialsException):
       await auth_service.login(dto)

@pytest.mark.asyncio
async def test_login_wrong_password(auth_service, mock_user_repo):
   hashed_pwd = hash_password("correct_password")
   user = UserModel(id=1, email="test@example.com", hashed_password=hashed_pwd, role=Role.USER.value)
   mock_user_repo.get_by_email.return_value = user

   dto = UserLoginSchema(email="test@example.com", password="wrong_password")
   with pytest.raises(InvalidCredentialsException):
       await auth_service.login(dto)


@pytest.mark.asyncio
async def test_refresh_access_token_success(auth_service):
   with patch("app.service.user_service.decode_refresh_token") as mock_decode, \
        patch("app.service.user_service.create_access_token") as mock_create_access:
      
       mock_decode.return_value = {
           "type": "refresh",
           "sub": "user@example.com",
           "user_id": 1,
           "role": "user"
       }
       mock_create_access.return_value = "new_access_token"


       res = await auth_service.refresh_access_token("valid_refresh_token")
       assert res["access_token"] == "new_access_token"
       assert res["refresh_token"] == "valid_refresh_token"
       assert res["role"] == "user"


@pytest.mark.asyncio
async def test_refresh_access_token_wrong_type(auth_service):
   with patch("app.service.user_service.decode_refresh_token") as mock_decode:
       mock_decode.return_value = {
           "type": "access",
           "sub": "user@example.com",
           "user_id": 1,
           "role": "user"
       }
       with pytest.raises(HTTPException) as exc_info:
           await auth_service.refresh_access_token("token_with_wrong_type")
       assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
       assert "Invalid Token Type" in exc_info.value.detail


@pytest.mark.asyncio
async def test_refresh_access_token_jwt_error(auth_service):
   with patch("app.service.user_service.decode_refresh_token", side_effect=jwt.PyJWTError):
       with pytest.raises(HTTPException) as exc_info:
           await auth_service.refresh_access_token("corrupt_token")
       assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
       assert "Invalid or expired refresh token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_profile_success(auth_service, mock_user_repo):
   user = UserModel(id=1, email="test@example.com", first_name="John")
   mock_user_repo.get_by_id.return_value = user

   profile = await auth_service.get_profile(1)
   assert profile == user

@pytest.mark.asyncio
async def test_get_profile_not_found(auth_service, mock_user_repo):
   mock_user_repo.get_by_id.return_value = None
   with pytest.raises(UserNotFoundException):
       await auth_service.get_profile(999)

@pytest.mark.asyncio
async def test_update_profile_success(auth_service, mock_user_repo):
   user = UserModel(id=1, email="test@example.com", first_name="John", last_name="Doe", phone_number="123")
   mock_user_repo.get_by_id.return_value = user
   mock_user_repo.update.return_value = user
   update_dto = UserProfileUpdateSchema(first_name="Jane", phone_number="456")
   updated = await auth_service.update_profile(1, update_dto)

   assert user.first_name == "Jane" # type: ignore
   assert user.phone_number == "456" # type: ignore
   assert user.last_name == "Doe" # type: ignore
   mock_user_repo.update.assert_called_once_with(user)


@pytest.mark.asyncio
async def test_update_profile_not_found(auth_service, mock_user_repo):
   mock_user_repo.get_by_id.return_value = None
   update_dto = UserProfileUpdateSchema(first_name="Jane")
   with pytest.raises(UserNotFoundException):
       await auth_service.update_profile(999, update_dto)

@pytest.mark.asyncio
async def test_request_password_reset_success(auth_service, mock_user_repo):
   user = UserModel(id=1, email="test@example.com")
   mock_user_repo.get_by_email.return_value = user
   bg_tasks = MagicMock(spec=BackgroundTasks)
   dto = ForgotPasswordRequestSchema(email="test@example.com")
   res = await auth_service.request_password_reset(dto, bg_tasks)
   assert "message" in res
   mock_user_repo.save_otp.assert_called_once()
   bg_tasks.add_task.assert_called_once()


@pytest.mark.asyncio
async def test_request_password_reset_user_not_found(auth_service, mock_user_repo):
   mock_user_repo.get_by_email.return_value = None
   bg_tasks = MagicMock(spec=BackgroundTasks)
   dto = ForgotPasswordRequestSchema(email="notfound@example.com")

   with pytest.raises(UserNotFoundException):
       await auth_service.request_password_reset(dto, bg_tasks)


@pytest.mark.asyncio
async def test_reset_password_success(auth_service, mock_user_repo):
   otp_record = PasswordResetModel(id=1, email="test@example.com", otp_code="123456", is_used=False)
   user = UserModel(id=1, email="test@example.com", hashed_password="old_hash")
  
   mock_user_repo.get_valid_otp.return_value = otp_record
   mock_user_repo.get_by_email.return_value = user

   dto = ResetPasswordRequestSchema(email="test@example.com", otp="123456", new_password="new_password123")
   res = await auth_service.reset_password(dto)


   assert "Password reset successfully" in res["message"]
   assert otp_record.is_used is True
   mock_user_repo.update.assert_called_once_with(user)
   mock_user_repo.save_otp.assert_called_once_with(otp_record)

@pytest.mark.asyncio
async def test_reset_password_invalid_otp(auth_service, mock_user_repo):
   mock_user_repo.get_valid_otp.return_value = None
   dto = ResetPasswordRequestSchema(email="test@example.com", otp="invalid_otp", new_password="new_password123")

   with pytest.raises(HTTPException) as exc_info:
       await auth_service.reset_password(dto)
   assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
   assert "Invalid or expired OTP" in exc_info.value.detail

@pytest.mark.asyncio
async def test_reset_password_user_missing(auth_service, mock_user_repo):
   otp_record = PasswordResetModel(id=1, email="test@example.com", otp_code="123456", is_used=False)
   mock_user_repo.get_valid_otp.return_value = otp_record
   mock_user_repo.get_by_email.return_value = None

   dto = ResetPasswordRequestSchema(email="test@example.com", otp="123456", new_password="new_password123")
   with pytest.raises(HTTPException) as exc_info:
       await auth_service.reset_password(dto)
   assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
   assert "User not found" in exc_info.value.detail
