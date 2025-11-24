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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )
