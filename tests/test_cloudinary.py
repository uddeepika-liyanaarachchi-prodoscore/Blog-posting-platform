import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from fastapi import UploadFile
from app.core.cloudinary_util import upload_image_to_cloudinary
from app.exceptions_handling.exceptions import CloudinaryConnectingError


def test_upload_image_to_cloudinary_success():
   fake_file = UploadFile(filename="test.png", file=BytesIO(b"fake image data"))
  
   with patch("cloudinary.uploader.upload") as mock_upload:
       mock_upload.return_value = {"secure_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpQQJkX4QxVH-28D1eFJ_RP7evdCNcec4wTA9wDIUwlw&s=10"}
       url = upload_image_to_cloudinary(fake_file)
       assert url == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpQQJkX4QxVH-28D1eFJ_RP7evdCNcec4wTA9wDIUwlw&s=10"
       mock_upload.assert_called_once_with(fake_file.file, folder="blog_posts")


def test_upload_image_to_cloudinary_failure():
   fake_file = UploadFile(filename="test.png", file=BytesIO(b"fake image data"))
  
   with patch("cloudinary.uploader.upload", side_effect=Exception("Connection to cloudinary failed")):
       with pytest.raises(CloudinaryConnectingError):
           upload_image_to_cloudinary(fake_file)
