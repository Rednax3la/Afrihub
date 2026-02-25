from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from bson import ObjectId
from database import get_db
from models.user import UserRegister, UserLogin, UserPublic, TokenResponse
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


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


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: UserRegister):
    db = get_db()

    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": body.name,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "location": body.location,
        "xp": 0,
        "streak": 0,
        "badges": 0,
        "avatar_url": None,
        "is_premium": False,
        "active_languages": [],
        "created_at": datetime.utcnow(),
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    token = create_access_token({"sub": str(result.inserted_id)})
    return TokenResponse(access_token=token, user=serialize_user(user_doc))


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    db = get_db()

    user = await db.users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=serialize_user(user))
