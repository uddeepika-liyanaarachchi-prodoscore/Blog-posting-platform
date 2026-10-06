import secrets
from email.message import EmailMessage
import aiosmtplib
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.exceptions_handling.exceptions import EnvLoadingError, OTPGeneratingError

def generate_otp() -> str:
    try:
        return str(secrets.randbelow(900000) + 100000)
    except Exception as e:
        raise OTPGeneratingError(f"Failed to generate OTP: {str(e)}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6),reraise=True)
async def send_otp_email(email: str, otp: str):
    sender_email = settings.GMAIL      
    sender_password = settings.GMAIL_SMTP_KEY  

    if not sender_email:
        raise EnvLoadingError("GMAIL environment variable is missing or empty")

    if not sender_password:
        raise EnvLoadingError("GMAIL_SMTP_KEY environment variable is missing or empty")

    msg = EmailMessage()
    msg["Subject"] = f"Your Verification Code: {otp}"  
    msg["From"] = sender_email
    msg["To"] = email
    msg.set_content(f"Your OTP code is: {otp}\nThis code will expire in 5 minutes.")

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            use_tls=True,
            username=sender_email,
            password=sender_password,
        )
        print(f"[SUCCESS] OTP {otp} sent successfully to {email}")

    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        raise RuntimeError(f"Email delivery failed: {str(e)}")
