import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.model.user_model import Role, UserModel  

async def seed_initial_admin(session: AsyncSession):
    admin_email = os.getenv("FIRST_ADMIN_EMAIL", "")
    admin_password = os.getenv("FIRST_ADMIN_PASSWORD", "")

    result = await session.execute(
        select(UserModel).where(UserModel.role == Role.ADMIN)
    )
    admin_exists = result.scalars().first()

    if not admin_exists:
        print(f"[*] Creating default Super Admin: {admin_email}...")
        
        default_admin = UserModel(
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role=Role.ADMIN.value,
        )
        session.add(default_admin)
        await session.commit()
        print("[✓] Default Admin created successfully!")
    else:
        print("[i] Admin user already exists. Skipping seed.")