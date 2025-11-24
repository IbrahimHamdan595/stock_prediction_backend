from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies.auth import authenticate_user, get_current_active_user
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.core.email import (
    generate_otp_code,
    generate_reset_token,
    verify_otp_code,
    get_otp_expiry_time,
    send_2fa_code,
    send_password_reset_email
)
from app.db.mongo import get_db
from app.schemas.auth import (
    Token,
    UserCreate,
    UserLogin,
    UserRead,
    Enable2FARequest,
    Verify2FARequest,
    Complete2FALogin,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest
)

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db=Depends(get_db)):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.utcnow()
    user_doc = {
        "_id": payload.email,
        "email": payload.email,
        "hashed_password": get_password_hash(payload.password),
        "full_name": payload.full_name,
        "role": "user",
        "is_active": True,
        "two_factor_enabled": False,
        "two_factor_secret": None,
        "two_factor_code": None,
        "two_factor_code_expires": None,
        "reset_token": None,
        "reset_token_expires": None,
        "created_at": now,
        "updated_at": now,
    }
    await db.users.insert_one(user_doc)
    return UserRead(**user_doc)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db=Depends(get_db)):
    user = await authenticate_user(payload.email, payload.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    # Check if 2FA is enabled
    if user.get("two_factor_enabled"):
        # Generate and send 2FA code
        code = generate_otp_code()
        expires_at = get_otp_expiry_time()

        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "two_factor_code": code,
                "two_factor_code_expires": expires_at
            }}
        )

        await send_2fa_code(user["email"], code)

        # Return token with 2FA requirement
        return Token(
            access_token="",
            refresh_token="",
            requires_2fa=True
        )

    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)
    access_token = create_access_token(str(user["_id"]), access_token_expires)
    refresh_token = create_refresh_token(str(user["_id"]), refresh_token_expires)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str, db=Depends(get_db)):
    from app.core.security import verify_token

    subject = verify_token(refresh_token, "refresh")
    access_token = create_access_token(subject)
    new_refresh = create_refresh_token(subject)
    return Token(access_token=access_token, refresh_token=new_refresh)


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_active_user)):
    return UserRead(**current_user.dict(by_alias=True))


# 2FA Endpoints
@router.post("/2fa/enable", status_code=status.HTTP_200_OK)
async def enable_2fa(payload: Enable2FARequest, db=Depends(get_db)):
    """Enable 2FA for a user and send verification code"""
    user = await db.users.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("two_factor_enabled"):
        raise HTTPException(status_code=400, detail="2FA is already enabled")

    # Generate and send code
    code = generate_otp_code()
    expires_at = get_otp_expiry_time()

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "two_factor_code": code,
            "two_factor_code_expires": expires_at
        }}
    )

    await send_2fa_code(user["email"], code)

    return {"message": "Verification code sent to your email"}


@router.post("/2fa/verify", status_code=status.HTTP_200_OK)
async def verify_2fa(payload: Verify2FARequest, db=Depends(get_db)):
    """Verify 2FA code and enable 2FA"""
    user = await db.users.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_otp_code(
        payload.code,
        user.get("two_factor_code"),
        user.get("two_factor_code_expires")
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    # Enable 2FA
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "two_factor_enabled": True,
            "two_factor_code": None,
            "two_factor_code_expires": None
        }}
    )

    return {"message": "2FA enabled successfully"}


@router.post("/2fa/disable", status_code=status.HTTP_200_OK)
async def disable_2fa(current_user=Depends(get_current_active_user), db=Depends(get_db)):
    """Disable 2FA for the current user"""
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {
            "two_factor_enabled": False,
            "two_factor_secret": None,
            "two_factor_code": None,
            "two_factor_code_expires": None
        }}
    )

    return {"message": "2FA disabled successfully"}


@router.post("/2fa/complete-login", response_model=Token)
async def complete_2fa_login(payload: Complete2FALogin, db=Depends(get_db)):
    """Complete login after 2FA verification"""
    user = await db.users.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.get("two_factor_enabled"):
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    if not verify_otp_code(
        payload.code,
        user.get("two_factor_code"),
        user.get("two_factor_code_expires")
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    # Clear the code
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "two_factor_code": None,
            "two_factor_code_expires": None
        }}
    )

    # Generate tokens
    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)
    access_token = create_access_token(str(user["_id"]), access_token_expires)
    refresh_token = create_refresh_token(str(user["_id"]), refresh_token_expires)

    return Token(access_token=access_token, refresh_token=refresh_token)


# Password Reset Endpoints
@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest, db=Depends(get_db)):
    """Request password reset - sends reset token via email"""
    user = await db.users.find_one({"email": payload.email})

    # Always return success to prevent email enumeration
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate reset token
    reset_token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expires": expires_at
        }}
    )

    await send_password_reset_email(user["email"], reset_token)

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(payload: ResetPasswordRequest, db=Depends(get_db)):
    """Reset password using the reset token"""
    user = await db.users.find_one({
        "reset_token": payload.token,
        "reset_token_expires": {"$gt": datetime.utcnow()}
    })

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Update password and clear reset token
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "hashed_password": get_password_hash(payload.new_password),
            "reset_token": None,
            "reset_token_expires": None
        }}
    )

    return {"message": "Password reset successfully"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_active_user),
    db=Depends(get_db)
):
    """Change password for authenticated user"""
    user = await db.users.find_one({"_id": current_user.id})

    if not verify_password(payload.current_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": get_password_hash(payload.new_password)}}
    )

    return {"message": "Password changed successfully"}
