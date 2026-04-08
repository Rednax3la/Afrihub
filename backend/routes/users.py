from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth import get_current_user
from routes.auth import serialize_user
from models.user import UserUpdate
from bson import ObjectId
from pydantic import BaseModel, EmailStr
import datetime

router = APIRouter(prefix="/api/users", tags=["users"])


class WaitlistEntry(BaseModel):
    email: EmailStr


@router.post("/waitlist", status_code=201)
async def join_waitlist(body: WaitlistEntry):
    db = get_db()
    await db.waitlist.update_one(
        {"email": body.email},
        {"$set": {"email": body.email, "joined_at": datetime.datetime.utcnow()}},
        upsert=True,
    )
    return {"message": "You're on the list!"}


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return serialize_user(current_user)


@router.patch("/me")
async def update_me(body: UserUpdate, current_user=Depends(get_current_user)):
    db = get_db()
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        return serialize_user(current_user)
    await db.users.update_one({"_id": current_user["_id"]}, {"$set": update_data})
    updated = await db.users.find_one({"_id": current_user["_id"]})
    return serialize_user(updated)


@router.post("/me/languages/{language_id}", status_code=200)
async def enroll_language(language_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$addToSet": {"active_languages": language_id}},
    )
    updated = await db.users.find_one({"_id": current_user["_id"]})
    return serialize_user(updated)
