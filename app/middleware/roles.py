# middleware/roles.py
from typing import List
from fastapi import Depends, HTTPException, status
from app.model.user_model import Role
from app.middleware.auth import authenticate

def authorize_roles(allowed_roles: List[Role]):
    async def role_checker(current_user: dict = Depends(authenticate)) -> dict:
        user_role = current_user.get("role")
        
        if user_role not in [role.value for role in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: You do not have permissions for this action. Allowed: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker