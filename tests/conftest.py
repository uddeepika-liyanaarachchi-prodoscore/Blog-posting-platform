import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock


# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
   sys.path.insert(0, PROJECT_ROOT)


# Set test environment variables
os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://root:password@localhost:3306/test_blog_db")
os.environ.setdefault("JWT_ACCESS_TOKEN", "test_access_secret_key_12345678901234567890")
os.environ.setdefault("JWT_REFRESH_TOKEN", "test_refresh_secret_key_12345678901234567890")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("GMAIL", "testuser@gmail.com")
os.environ.setdefault("GMAIL_SMTP_KEY", "test_smtp_key")
os.environ.setdefault("FIRST_ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("FIRST_ADMIN_PASSWORD", "admin1234")
os.environ.setdefault("CLOUDINARY_CLOUD_NAME", "test_cloud")
os.environ.setdefault("CLOUDINARY_API_KEY", "test_api_key")
os.environ.setdefault("CLOUDINARY_API_SECRET", "test_api_secret")


@pytest.fixture
def mock_async_session():
   """Mock AsyncSession for database operations"""
   session = AsyncMock()
   session.add = MagicMock()
   session.commit = AsyncMock()
   session.refresh = AsyncMock()
   session.close = AsyncMock()
   session.execute = AsyncMock()
   return session
