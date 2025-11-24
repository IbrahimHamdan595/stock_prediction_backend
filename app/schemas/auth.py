from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    requires_2fa: bool = False


class TokenPayload(BaseModel):
    sub: str
    type: str
    exp: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    two_factor_enabled: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}


# 2FA schemas
class Enable2FARequest(BaseModel):
    email: EmailStr


class Verify2FARequest(BaseModel):
    email: EmailStr
    code: str


class Complete2FALogin(BaseModel):
    email: EmailStr
    code: str


# Password reset schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)
