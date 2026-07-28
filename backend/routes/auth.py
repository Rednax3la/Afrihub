import logging
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from bson import ObjectId
from database import get_db
from models.user import UserRegister, TutorRegister, UserLogin, UserPublic, TokenResponse
from auth import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def serialize_user(user: dict) -> UserPublic:
    return UserPublic(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        role=user.get("role", "student"),
        location=user.get("location"),
        xp=user.get("xp", 0),
        streak=user.get("streak", 0),
        badges=user.get("badges", 0),
        earned_badges=user.get("earned_badges", []),
        avatar_url=user.get("avatar_url"),
        is_premium=user.get("is_premium", False),
        active_languages=user.get("active_languages", []),
        created_at=user.get("created_at", datetime.utcnow()),
        language_xp=user.get("language_xp", {}),
        bio=user.get("bio"),
        languages_taught=user.get("languages_taught", []),
        tutor_status=user.get("tutor_status"),
        voice_character=user.get("voice_character"),
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
        "role": "student",
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


@router.post("/register/tutor", response_model=TokenResponse, status_code=201)
async def register_tutor(body: TutorRegister):
    db = get_db()
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": body.name,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "location": body.location,
        "role": "tutor",
        "tutor_status": "pending",
        "bio": body.bio,
        "languages_taught": body.languages_taught,
        "voice_character": body.voice_character,
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
    logger.info("Login attempt for email=%s", body.email)

    user = await db.users.find_one({"email": body.email})
    logger.info("Login lookup for email=%s found_user=%s", body.email, bool(user))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    password_hash = user.get("password_hash")
    logger.debug(
        "Login for email=%s password_hash_prefix=%s",
        body.email,
        password_hash[:20] if password_hash else None,
    )
    logger.debug(
        "Login for email=%s plaintext_password_length=%s",
        body.email,
        len(body.password) if body.password else 0,
    )

    if not password_hash:
        logger.info("Login failed for email=%s: no password_hash stored", body.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    verify_result = verify_password(body.password, password_hash)
    logger.info("Login verify_password result for email=%s: %s", body.email, verify_result)

    if not verify_result:
        logger.info(
            "Password verification failed for email=%s plaintext_length=%s hash_length=%s",
            body.email,
            len(body.password) if body.password else 0,
            len(password_hash) if password_hash else 0,
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"])})
    return TokenResponse(access_token=token, user=serialize_user(user))
