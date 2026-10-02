from fastapi import Request,status
from fastapi.responses import JSONResponse

from app.exceptions_handling.exceptions import AppExceptions


class PostsNotFoundException(AppExceptions):
    def __init__(self,identifier:str|int|None):
        self.identifier = identifier

        message = (
            f"Post are not found with ID: {identifier}"
            if identifier
            else "Requested post could not be found."
        )
        super().__init__(message)

async def user_already_exists_handler(request: Request, exc: PostsNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)}
    )
