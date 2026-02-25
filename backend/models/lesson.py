from pydantic import BaseModel
from typing import List, Optional


class AnswerOption(BaseModel):
    id: str
    text: str


class Question(BaseModel):
    id: str
    type: str  # "translate" | "multiple_choice" | "listen"
    prompt: str          # The foreign phrase or question text
    native_text: Optional[str] = None  # English equivalent (for display)
    options: List[AnswerOption]
    correct_answer_id: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None


class Lesson(BaseModel):
    id: str
    unit_id: str
    title: str
    description: Optional[str] = None
    order: int
    xp_reward: int = 10
    questions: List[Question] = []


class Unit(BaseModel):
    id: str
    language_id: str
    title: str
    subtitle: str
    icon: str
    order: int
    lessons: List[dict] = []  # lightweight lesson summaries


class Language(BaseModel):
    id: str
    name: str
    code: str  # e.g. "yo", "sw", "zu"
    country: str
    flag_emoji: str
    color: str        # Tailwind color for UI
    speaker_count: str
    description: str
    is_free: bool = True


class AnswerSubmit(BaseModel):
    lesson_id: str
    question_id: str
    answer_id: str


class AnswerResult(BaseModel):
    correct: bool
    correct_answer_id: str
    xp_earned: int
