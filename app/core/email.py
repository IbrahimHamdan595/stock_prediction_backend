import secrets
from datetime import datetime, timedelta
from typing import Optional

import pyotp


def generate_otp_code(length: int = 6) -> str:
    """Generate a random OTP code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def generate_reset_token() -> str:
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


def verify_otp_code(code: str, stored_code: str, expires_at: Optional[datetime]) -> bool:
    """Verify OTP code and expiration"""
    if not stored_code or not expires_at:
        return False

    if datetime.utcnow() > expires_at:
        return False

    return code == stored_code


def get_otp_expiry_time(minutes: int = 10) -> datetime:
    """Get expiry time for OTP (default 10 minutes)"""
    return datetime.utcnow() + timedelta(minutes=minutes)


async def send_email_mock(to_email: str, subject: str, body: str) -> bool:
    """
    Mock email sender for development.
    In production, replace with actual email service (SendGrid, AWS SES, etc.)
    """
    print(f"\n{'='*60}")
    print(f"📧 EMAIL SENT")
    print(f"{'='*60}")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print(f"{'='*60}\n")
    return True


async def send_2fa_code(email: str, code: str) -> bool:
    """Send 2FA code via email"""
    subject = "Your 2FA Verification Code"
    body = f"""
Hello,

Your two-factor authentication code is: {code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
StockPredict Team
    """
    return await send_email_mock(email, subject, body)


async def send_password_reset_email(email: str, token: str, frontend_url: str = "http://localhost:3000") -> bool:
    """Send password reset email with token"""
    reset_link = f"{frontend_url}/auth/reset-password?token={token}"
    subject = "Password Reset Request"
    body = f"""
Hello,

You requested to reset your password. Click the link below to reset your password:

{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
StockPredict Team
    """
    return await send_email_mock(email, subject, body)
