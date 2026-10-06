import os
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from app.exceptions_handling.exceptions import CloudinaryConnectingError

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6),reraise=True)
def upload_image_to_cloudinary(file: UploadFile) -> str:
    try:
        result = cloudinary.uploader.upload(file.file, folder="blog_posts")
        return result.get("secure_url")
    except Exception as e:
        raise CloudinaryConnectingError()