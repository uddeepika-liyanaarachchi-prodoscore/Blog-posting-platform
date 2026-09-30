import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str=os.getenv("DATABASE_URL", "")
    JWT_ACCESS_TOKEN: str=os.getenv("JWT_ACCESS_TOKEN","")
    JWT_REFRESH_TOKEN: str=os.getenv("JWT_REFRESH_TOKEN","")
    REFRESH_TOKEN_EXPIRE_MINUTES: int=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES",""))
    ACCESS_TOKEN_EXPIRE_MINUTES: int=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",""))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM","")

settings = Settings()