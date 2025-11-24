import asyncio

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password


def test_password_hash_roundtrip():
    password = "strongpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)


def test_access_token_contains_subject():
    token = create_access_token("user-id")
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert payload["sub"] == "user-id"
    assert payload["type"] == "access"
