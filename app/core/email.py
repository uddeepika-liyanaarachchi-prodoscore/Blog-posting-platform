import secrets

def generate_otp() -> str:
    # 6-digit cryptographically secure OTP
    return f"{secrets.randbelow(900000) + 100000}"

async def send_otp_email(email: str, otp: str):
    print(f"\n[EMAIL SERVICE] Sending OTP {otp} to {email}...\n")