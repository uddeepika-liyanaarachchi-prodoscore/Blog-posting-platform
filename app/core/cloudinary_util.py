import os
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from dotenv import load_dotenv

from app.exceptions_handling.exceptions import CloudinaryConnectingError

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_image_to_cloudinary(file: UploadFile) -> str:
    try:
        result = cloudinary.uploader.upload(file.file, folder="blog_posts")
        return result.get("secure_url")
    except Exception as e:
        raise CloudinaryConnectingError()