from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database import get_db
from auth import get_current_user
from models.user import UserPublic
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["users"])


def serialize_user(user: dict) -> UserPublic:
    return UserPublic(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        location=user.get("location"),
        xp=user.get("xp", 0),
        streak=user.get("streak", 0),
        badges=user.get("badges", 0),
        avatar_url=user.get("avatar_url"),
        is_premium=user.get("is_premium", False),
        active_languages=user.get("active_languages", []),
        created_at=user.get("created_at", datetime.utcnow()),
    )


@router.get("/me", response_model=UserPublic)
async def get_me(current_user=Depends(get_current_user)):
    return serialize_user(current_user)


@router.patch("/me")
async def update_profile(updates: dict, current_user=Depends(get_current_user)):
    db = get_db()
    allowed_fields = {"name", "location", "avatar_url"}
    filtered = {k: v for k, v in updates.items() if k in allowed_fields}

    if not filtered:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    await db.users.update_one(
        {"_id": ObjectId(str(current_user["_id"]))},
        {"$set": filtered}
    )
    updated = await db.users.find_one({"_id": ObjectId(str(current_user["_id"]))})
    return serialize_user(updated)


@router.post("/me/languages/{language_id}")
async def enroll_language(language_id: str, current_user=Depends(get_current_user)):
    """Add a language to the user's active learning list."""
    db = get_db()

    language = await db.languages.find_one({"id": language_id})
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")

    active = current_user.get("active_languages", [])
    if language_id not in active:
        active.append(language_id)
        await db.users.update_one(
            {"_id": ObjectId(str(current_user["_id"]))},
            {"$set": {"active_languages": active}}
        )

    return {"message": f"Enrolled in {language['name']}", "active_languages": active}
