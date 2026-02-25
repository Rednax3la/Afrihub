from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LessonProgress(BaseModel):
    lesson_id: str
    completed: bool = False
    score: int = 0       # percentage correct
    attempts: int = 0
    last_attempted: Optional[datetime] = None


class UnitProgress(BaseModel):
    unit_id: str
    lessons_completed: int = 0
    total_lessons: int = 0
    progress_percent: float = 0.0


class LanguageProgress(BaseModel):
    language_id: str
    language_name: str
    xp: int = 0
    percent_complete: float = 0.0
    current_unit: str = ""
    current_lesson: str = ""
    units: List[UnitProgress] = []


class UserProgress(BaseModel):
    user_id: str
    languages: List[LanguageProgress] = []
    updated_at: datetime
