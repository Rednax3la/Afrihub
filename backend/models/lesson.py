from pydantic import BaseModel
from typing import List, Optional


class AnswerOption(BaseModel):
    id: str
    text: str


class Question(BaseModel):
    id: str
    type: str  # "translate" | "multiple_choice" | "listen" | "image"
    prompt: str
    native_text: Optional[str] = None
    options: List[AnswerOption] = []
    correct_answer_id: str
    audio_url: Optional[str] = None   # For listen questions or pronunciation aid
    image_url: Optional[str] = None   # For image questions


class Lesson(BaseModel):
    id: str
    unit_id: str
    language_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    order: int = 1
    xp_reward: int = 10
    questions: List[Question] = []
    status: str = "published"                   # "draft" | "published"
    audio_intro_url: Optional[str] = None       # Optional lesson intro audio
    cultural_note: Optional[str] = None         # Cultural context shown after lesson
    cultural_note_title: Optional[str] = None


class Unit(BaseModel):
    id: str
    language_id: str
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    order: int = 1
    lessons: List[dict] = []
    cultural_context: Optional[str] = None     # Brief background for this unit


class Language(BaseModel):
    id: str
    name: str
    code: str
    country: str
    flag_emoji: str
    color: str = "emerald"
    speaker_count: str = ""
    description: str = ""
    is_free: bool = True


class AnswerSubmit(BaseModel):
    lesson_id: str
    question_id: str
    answer_id: str


class AnswerResult(BaseModel):
    correct: bool
    correct_answer_id: str
    xp_earned: int = 0
