from datetime import datetime
from enum import Enum
from typing import Optional

from bson import ObjectId
from pydantic import ConfigDict, EmailStr, Field

from app.models.base import MongoModel


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    read_only = "read_only"


class User(MongoModel):
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.user)
    is_active: bool = True

    # 2FA fields
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    two_factor_code: Optional[str] = None
    two_factor_code_expires: Optional[datetime] = None

    # Password reset fields
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
