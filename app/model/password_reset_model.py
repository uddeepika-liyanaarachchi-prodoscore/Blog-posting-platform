from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.core.db import Base

class PasswordResetModel(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)