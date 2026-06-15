from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, RoleEnum
from app.services.audit import AuditService
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None
    role: RoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    await AuditService.log_action(
        db=db,
        action="user_registered",
        entity_type="User",
        entity_id=str(user.id),
        user_id=user.id,
        user_email=user.email,
        user_role=user.role.value
    )
    
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    await AuditService.log_action(
        db=db,
        action="user_logged_in",
        entity_type="User",
        entity_id=str(user.id),
        user_id=user.id,
        user_email=user.email,
        user_role=user.role.value
    )
        
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


import uuid
from app.api.deps import get_current_user
from datetime import timedelta
from jose import jwt, JWTError

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    password: str | None = None

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

import secrets
import hashlib
from datetime import timedelta, datetime, timezone
from app.models.user import User, PasswordResetToken
from app.services.email import email_service
from fastapi import Request

from app.core.rate_limit import limiter

@router.post("/forgot-password")
@limiter.limit("5/hour")
async def forgot_password(request: Request, payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    
    # Generic success message to prevent email enumeration
    success_msg = "If an account exists for this email, a password reset link has been sent."
    
    if user:
        # Generate raw secure token
        raw_token = secrets.token_urlsafe(32)
        # Hash token for database
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        
        # Invalidate previous tokens by setting them expired
        now = datetime.now(timezone.utc)
        await db.execute(
            select(PasswordResetToken)
            .filter(PasswordResetToken.user_id == user.id)
            .filter(PasswordResetToken.used_at.is_(None))
        )
        # For simplicity, we just insert a new one and check expiration during verification
        
        expires_at = now + timedelta(minutes=30)
        
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.add(reset_token)
        await db.commit()
        
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
        await email_service.send_password_reset(user.email, reset_link)

    return {"message": success_msg}

@router.post("/reset-password")
@limiter.limit("10/hour")
async def reset_password(request: Request, payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Basic password strength check
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
    token_hash = hashlib.sha256(payload.token.encode('utf-8')).hexdigest()
    
    result = await db.execute(
        select(PasswordResetToken)
        .where(PasswordResetToken.token_hash == token_hash)
        .where(PasswordResetToken.used_at.is_(None))
    )
    reset_token = result.scalar_one_or_none()
    
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    now = datetime.now(timezone.utc)
    # Be flexible with naive datetime comparisons depending on postgres config
    if reset_token.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="Reset token has expired")
        
    result_user = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = result_user.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
        
    # Update password and mark token used
    user.password_hash = get_password_hash(payload.new_password)
    reset_token.used_at = now
    
    # Invalidate all other active tokens for this user
    # Simplified: just commit
    await db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/update-profile", response_model=UserOut)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.password:
        current_user.password_hash = get_password_hash(payload.password)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

