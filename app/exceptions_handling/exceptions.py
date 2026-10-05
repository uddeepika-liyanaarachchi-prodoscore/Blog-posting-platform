class AppExceptions(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ==========================================
# 1. USER & AUTHENTICATION EXCEPTIONS
# ==========================================

class UserAlreadyExistsException(AppExceptions):
    def __init__(self, email: str):
        self.email = email
        super().__init__(
            message=f"User with email '{email}' already exists.", 
            status_code=409
        )

class UserNotFoundException(AppExceptions):
    def __init__(self, identifier: str | int | None = None):
        msg = f"User not found with ID/Email: {identifier}" if identifier else "User does not exist."
        super().__init__(message=msg, status_code=404)

class InvalidCredentialsException(AppExceptions):
    def __init__(self, message: str = "Invalid email or password."):
        super().__init__(message=message, status_code=401)

class TokenExpiredException(AppExceptions):
    def __init__(self, message: str = "Token has expired. Please login again."):
        super().__init__(message=message, status_code=401)

class InvalidTokenException(AppExceptions):
    def __init__(self, message: str = "Invalid or malformed token."):
        super().__init__(message=message, status_code=401)

class PasswordResetTokenInvalidException(AppExceptions):
    def __init__(self, message: str = "Password reset link is invalid or has expired."):
        super().__init__(message=message, status_code=400)

class AccountInactiveException(AppExceptions):
    def __init__(self, message: str = "This account has been deactivated."):
        super().__init__(message=message, status_code=403)


# ==========================================
# 2. POSTS DOMAIN EXCEPTIONS
# ==========================================

class PostsNotFoundException(AppExceptions):
    def __init__(self, identifier: str | int | None = None):
        msg = f"Post not found with ID: {identifier}" if identifier else "Requested post not found."
        super().__init__(message=msg, status_code=404)

class PostAccessDeniedException(AppExceptions):
    def __init__(self, message: str = "You do not have permission to modify this post."):
        super().__init__(message=message, status_code=403)

class InvalidPostStatusException(AppExceptions):
    def __init__(self, msg: str = "Invalid status transition for this post."):
        super().__init__(message=msg, status_code=400)

class InvalidPostsType(AppExceptions):
    def __init__(self, msg: str = "Invalid type ."):
        super().__init__(message=msg, status_code=422)


class PostAlreadyDeletedException(AppExceptions):
    def __init__(self, identifier: int | str):
        super().__init__(
            message=f"Post with ID {identifier} is deleted and cannot be modified.", 
            status_code=400
        )


# ==========================================
# 3. FILE / MEDIA UPLOAD EXCEPTIONS
# ==========================================

class InvalidFileFormatException(AppExceptions):
    def __init__(self, message: str = "Only JPEG, PNG and WebP images are allowed."):
        super().__init__(message=message, status_code=415)

class FileSizeExceededException(AppExceptions):
    def __init__(self, max_size_mb: int = 5):
        super().__init__(
            message=f"Image size exceeds the maximum limit of {max_size_mb}MB.", 
            status_code=413
        )

class ImageUploadFailedException(AppExceptions):
    def __init__(self, message: str = "Failed to upload media to cloud storage. Please try again."):
        super().__init__(message=message, status_code=502)

class CloudinaryConnectingError(AppExceptions):
    def __init__(self, message: str = "Failed conneting to cloudinary storage. Please try again."):
        super().__init__(message=message, status_code=502)


# ==========================================
# 4. Config Values 
# ==========================================

class EnvLoadingError(AppExceptions):
    def __init__(self, message: str = "Failed to load config values. check your environtment variables and try again."):
        super().__init__(message=message, status_code=500)


# ==========================================
# 5. Email sending related
# ==========================================

class OTPGeneratingError(AppExceptions):
    def __init__(self, message: str = "Failed to load the OTP."):
        super().__init__(message=message, status_code=500)

class SendingEmailFailed(AppExceptions):
    def __init__(self, message: str = "Failed to send the email."):
        super().__init__(message=message, status_code=502)

