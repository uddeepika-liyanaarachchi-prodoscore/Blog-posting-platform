import pytest
from app.exceptions_handling.exceptions import (
   AppExceptions,
   UserAlreadyExistsException,
   UserNotFoundException,
   InvalidCredentialsException,
   TokenExpiredException,
   InvalidTokenException,
   PasswordResetTokenInvalidException,
   AccountInactiveException,
   PostsNotFoundException,
   PostAccessDeniedException,
   InvalidPostStatusException,
   PostAlreadyDeletedException,
   InvalidFileFormatException,
   FileSizeExceededException,
   ImageUploadFailedException,
   CloudinaryConnectingError,
   EnvLoadingError,
   OTPGeneratingError,
   SendingEmailFailed,
)


def test_app_exceptions_base():
   exc = AppExceptions(message="Base error", status_code=400)
   assert exc.message == "Base error"
   assert exc.status_code == 400


def test_user_exceptions():
   exc1 = UserAlreadyExistsException(email="user@test.com")
   assert exc1.status_code == 409
   assert exc1.email == "user@test.com"
   assert "user@test.com" in exc1.message


   exc2 = UserNotFoundException(identifier="123")
   assert exc2.status_code == 404
   assert "123" in exc2.message


   exc2_empty = UserNotFoundException()
   assert exc2_empty.status_code == 404
   assert exc2_empty.message == "User does not exist."


   exc3 = InvalidCredentialsException()
   assert exc3.status_code == 401


   exc4 = TokenExpiredException()
   assert exc4.status_code == 401


   exc5 = InvalidTokenException()
   assert exc5.status_code == 401


   exc6 = PasswordResetTokenInvalidException()
   assert exc6.status_code == 400


   exc7 = AccountInactiveException()
   assert exc7.status_code == 403


def test_posts_exceptions():
   exc1 = PostsNotFoundException(identifier=10)
   assert exc1.status_code == 404
   assert "10" in exc1.message


   exc1_empty = PostsNotFoundException()
   assert exc1_empty.status_code == 404
   assert exc1_empty.message == "Requested post not found."


   exc2 = PostAccessDeniedException()
   assert exc2.status_code == 403


   exc3 = InvalidPostStatusException()
   assert exc3.status_code == 400


   exc4 = PostAlreadyDeletedException(identifier=15)
   assert exc4.status_code == 400
   assert "15" in exc4.message


def test_media_and_system_exceptions():
   exc1 = InvalidFileFormatException()
   assert exc1.status_code == 415


   exc2 = FileSizeExceededException(max_size_mb=10)
   assert exc2.status_code == 413
   assert "10MB" in exc2.message


   exc3 = ImageUploadFailedException()
   assert exc3.status_code == 502


   exc4 = CloudinaryConnectingError()
   assert exc4.status_code == 502


   exc5 = EnvLoadingError()
   assert exc5.status_code == 500


   exc6 = OTPGeneratingError()
   assert exc6.status_code == 500


   exc7 = SendingEmailFailed()
   assert exc7.status_code == 502
