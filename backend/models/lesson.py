from pydantic import BaseModel
from typing import List, Optional


class AnswerOption(BaseModel):
    id: str
    text: Optional[str] = None        # None for image_match options
    image_url: Optional[str] = None   # For image_match options


class Question(BaseModel):
    id: str
    # "translate" | "multiple_choice" | "listen" | "image"
    # "listen_comprehension" | "image_translate" | "image_match"
    type: str
    prompt: str
    native_text: Optional[str] = None
    options: List[AnswerOption] = []
    correct_answer_id: str
    audio_url: Optional[str] = None   # For listen / listen_comprehension / pronunciation aid
    image_url: Optional[str] = None   # For image / image_translate questions
    video_url: Optional[str] = None   # For video lessons/questions


class Lesson(BaseModel):
    id: str
    unit_id: str
    language_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    order: int = 1
    xp_reward: int = 10
    questions: List[Question] = []
    status: str = "published"                   # "draft" | "published" | "pending_review" | "rejected"
    source: Optional[str] = None               # "tutor" | "scraped"
    audio_intro_url: Optional[str] = None
    cultural_note: Optional[str] = None
    cultural_note_title: Optional[str] = None


class Unit(BaseModel):
    id: str
    language_id: str
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    order: int = 1
    lessons: List[dict] = []
    cultural_context: Optional[str] = None


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


class CulturalNote(BaseModel):
    language_id: str
    title: str
    body: str
    category: str = "tradition"   # "proverb" | "tradition" | "history" | "etymology"
    related_unit_ids: List[str] = []
    source: str = "tutor"         # "tutor" | "scraped"
