import pytest
from unittest.mock import patch, AsyncMock
from app.core.email import generate_otp, send_otp_email
from app.exceptions_handling.exceptions import EnvLoadingError, OTPGeneratingError
from app.core.config import settings


def test_generate_otp_success():
   otp = generate_otp()
   assert isinstance(otp, str)
   assert len(otp) == 6
   assert otp.isdigit()


def test_generate_otp_failure():
   with patch("secrets.randbelow", side_effect=Exception("Random error")):
       with pytest.raises(OTPGeneratingError):
           generate_otp()


@pytest.mark.asyncio
async def test_send_otp_email_success():
   with patch.object(settings, "GMAIL", "sender@gmail.com"), \
        patch.object(settings, "GMAIL_SMTP_KEY", "app_password"), \
        patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
      
       await send_otp_email("recipient@example.com", "123456")
       assert mock_send.called
       assert mock_send.call_count == 1
       call_args, call_kwargs = mock_send.call_args
       assert call_kwargs["hostname"] == "smtp.gmail.com"
       assert call_kwargs["port"] == 465
       assert call_kwargs["username"] == "sender@gmail.com"
       assert call_kwargs["password"] == "app_password"


@pytest.mark.asyncio
async def test_send_otp_email_missing_gmail():
   with patch.object(settings, "GMAIL", ""):
       with pytest.raises(EnvLoadingError, match="GMAIL environment variable is missing"):
           await send_otp_email("recipient@example.com", "123456")


@pytest.mark.asyncio
async def test_send_otp_email_missing_smtp_key():
   with patch.object(settings, "GMAIL", "sender@gmail.com"), \
        patch.object(settings, "GMAIL_SMTP_KEY", ""):
       with pytest.raises(EnvLoadingError, match="GMAIL_SMTP_KEY environment variable is missing"):
           await send_otp_email("recipient@example.com", "123456")


@pytest.mark.asyncio
async def test_send_otp_email_smtp_failure():
   with patch.object(settings, "GMAIL", "sender@gmail.com"), \
        patch.object(settings, "GMAIL_SMTP_KEY", "app_password"), \
        patch("aiosmtplib.send", side_effect=Exception("SMTP Connection error")):
      
       with pytest.raises(RuntimeError, match="Email delivery failed"):
           await send_otp_email("recipient@example.com", "123456")



