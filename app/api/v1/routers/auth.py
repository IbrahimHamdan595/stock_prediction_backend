from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies.auth import authenticate_user, get_current_active_user
from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.db.mongo import get_db
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db=Depends(get_db)):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_doc = {
        "_id": payload.email,
        "email": payload.email,
        "hashed_password": get_password_hash(payload.password),
        "full_name": payload.full_name,
        "role": "user",
        "is_active": True,
    }
    await db.users.insert_one(user_doc)
    return UserRead(**user_doc)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db=Depends(get_db)):
    user = await authenticate_user(payload.email, payload.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)
    access_token = create_access_token(str(user.id), access_token_expires)
    refresh_token = create_refresh_token(str(user.id), refresh_token_expires)
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
