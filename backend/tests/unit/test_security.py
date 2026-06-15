import pytest
from datetime import timedelta
from jose import jwt
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_supabase_jwt,
)
from app.core.config import settings

def test_password_hash_and_verify():
    password = "supersecretpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token_contains_subject():
    subject = "user123"
    token = create_access_token(subject)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == subject
    assert "exp" in payload

def test_create_access_token_with_custom_expiry():
    subject = "user123"
    expires_delta = timedelta(minutes=5)
    token = create_access_token(subject, expires_delta=expires_delta)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == subject

def test_decode_supabase_jwt_invalid():
    assert decode_supabase_jwt("invalid.token.string") is None
