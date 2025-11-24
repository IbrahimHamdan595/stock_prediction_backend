from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies.auth import get_current_admin
from app.db.mongo import get_db
from app.models.user import User
from app.schemas.auth import UserRead

router = APIRouter()


@router.get("/", response_model=list[UserRead])
async def list_users(db=Depends(get_db), admin=Depends(get_current_admin)):
    users = [User(**doc) async for doc in db.users.find()]
    return [UserRead(**u.dict(by_alias=True)) for u in users]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db=Depends(get_db), admin=Depends(get_current_admin)):
    doc = await db.users.find_one({"_id": user_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead(**doc)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: str, payload: dict, db=Depends(get_db), admin=Depends(get_current_admin)):
    result = await db.users.find_one_and_update({"_id": user_id}, {"$set": payload}, return_document=True)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead(**result)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db=Depends(get_db), admin=Depends(get_current_admin)):
    await db.users.delete_one({"_id": user_id})
    return None
