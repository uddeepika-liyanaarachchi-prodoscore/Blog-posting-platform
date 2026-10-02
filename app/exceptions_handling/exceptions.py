from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppExceptions(Exception):
    pass

class UserAlreadyExistsException(AppExceptions):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists.")

class InvalidPasswordException(AppExceptions):
    def __init__(self,email:str):
        self.email = email
        super().__init__(f"Invalid Password")

async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": str(exc)}
    )

async def username_password_invalicd_handler(request:Request, exc: InvalidPasswordException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message":str(exc)}
    )

