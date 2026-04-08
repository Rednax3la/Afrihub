from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    location: Optional[str] = None


class TutorRegister(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    location: Optional[str] = None
    bio: str = ""
    languages_taught: List[str] = []
    voice_character: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    voice_character: Optional[str] = None


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    is_premium: Optional[bool] = None
    role: Optional[str] = None
    location: Optional[str] = None


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    role: str = "student"
    location: Optional[str] = None
    xp: int = 0
    streak: int = 0
    badges: int = 0
    earned_badges: List[str] = []
    avatar_url: Optional[str] = None
    is_premium: bool = False
    active_languages: List[str] = []
    created_at: datetime
    # Tutor-specific fields (None for students)
    bio: Optional[str] = None
    languages_taught: List[str] = []
    tutor_status: Optional[str] = None  # "pending" | "active" | "suspended"
    voice_character: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
