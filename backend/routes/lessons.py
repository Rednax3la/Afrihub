from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth import get_current_user
from models.lesson import AnswerSubmit, AnswerResult
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
import datetime

router = APIRouter(prefix="/api", tags=["lessons"])

_PUBLISHED_FILTER = {"$nin": ["draft", "rejected", "pending_review"]}


# ── Languages ──────────────────────────────────────────────────────────────────

@router.get("/languages")
async def list_languages():
    db = get_db()
    languages = await db.languages.find().to_list(100)
    for lang in languages:
        lang["_id"] = str(lang["_id"])
    return languages


@router.get("/languages/{language_id}")
async def get_language(language_id: str):
    db = get_db()
    lang = await db.languages.find_one({"id": language_id})
    if not lang:
        raise HTTPException(status_code=404, detail="Language not found")
    lang["_id"] = str(lang["_id"])
    return lang


# ── Cultural Notes ─────────────────────────────────────────────────────────────

@router.get("/languages/{language_id}/cultural-notes")
async def list_cultural_notes(language_id: str):
    db = get_db()
    notes = await db.cultural_notes.find({"language_id": language_id}).sort("_id", 1).to_list(200)
    for note in notes:
        note["_id"] = str(note["_id"])
    return notes


# ── Leaderboard ────────────────────────────────────────────────────────────────

@router.get("/leaderboard/{language_id}")
async def get_leaderboard(language_id: str):
    """Phase 3 scaffold: top 20 users by XP (language-specific XP tracking is a future enhancement)."""
    db = get_db()
    # Only users who have this language active
    users = await db.users.find(
        {"active_languages": language_id, "role": {"$nin": ["admin", "tutor"]}},
        {"name": 1, "xp": 1, "streak": 1, "avatar_url": 1}
    ).sort("xp", -1).to_list(20)
    return [
        {
            "id": str(u["_id"]),
            "name": u.get("name", "Learner"),
            "xp": u.get("xp", 0),
            "streak": u.get("streak", 0),
            "avatar_url": u.get("avatar_url"),
        }
        for u in users
    ]


# ── Units (with embedded lessons for dashboard) ────────────────────────────────

@router.get("/languages/{language_id}/units")
async def list_units(language_id: str):
    db = get_db()
    units = await db.units.find({"language_id": language_id}).sort("order", 1).to_list(50)
    result = []
    for unit in units:
        unit["_id"] = str(unit["_id"])
        lessons = await db.lessons.find(
            {"unit_id": unit["id"], "status": _PUBLISHED_FILTER},
            {"questions": 0}
        ).sort("order", 1).to_list(50)
        for lesson in lessons:
            lesson.pop("_id", None)
        if lessons:  # only include units that have at least one published lesson
            unit["lessons"] = lessons
            result.append(unit)
    return result


# ── Lessons ────────────────────────────────────────────────────────────────────

@router.get("/units/{unit_id}/lessons")
async def list_lessons(unit_id: str):
    db = get_db()
    lessons = await db.lessons.find(
        {"unit_id": unit_id, "status": _PUBLISHED_FILTER},
        {"questions": 0}
    ).sort("order", 1).to_list(50)
    for lesson in lessons:
        lesson["_id"] = str(lesson["_id"])
    return lessons


@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson or lesson.get("status") in ("draft", "rejected", "pending_review"):
        raise HTTPException(status_code=404, detail="Lesson not found")
    lesson["_id"] = str(lesson["_id"])
    for q in lesson.get("questions", []):
        q.pop("correct_answer_id", None)
    # Inject language_code (e.g. "yo") so the frontend TTS system has the right BCP-47 code.
    # Lessons store unit_id, not language_id directly, so we walk unit → language.
    if lesson.get("unit_id"):
        unit = await db.units.find_one({"id": lesson["unit_id"]}, {"language_id": 1})
        if unit:
            lang = await db.languages.find_one(
                {"id": unit["language_id"]}, {"code": 1, "id": 1}
            )
            if lang:
                lesson["language_code"] = lang.get("code")
                lesson["language_id"] = unit["language_id"]
    return lesson


# ── Answer Submission ──────────────────────────────────────────────────────────

@router.post("/lessons/answer", response_model=AnswerResult)
async def submit_answer(body: AnswerSubmit, current_user=Depends(get_current_user)):
    db = get_db()

    lesson = await db.lessons.find_one({"id": body.lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    question = next((q for q in lesson["questions"] if q["id"] == body.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    correct = question["correct_answer_id"] == body.answer_id
    xp_earned = lesson.get("xp_reward", 10) if correct else 0

    if correct:
        await db.users.update_one(
            {"_id": ObjectId(str(current_user["_id"]))},
            {"$inc": {"xp": xp_earned}}
        )

    await db.progress.update_one(
        {"user_id": str(current_user["_id"]), "lesson_id": body.lesson_id},
        {
            "$inc": {"attempts": 1},
            "$set": {"last_attempted": datetime.datetime.utcnow()},
            "$setOnInsert": {"completed": False, "score": 0},
        },
        upsert=True
    )

    return AnswerResult(
        correct=correct,
        correct_answer_id=question["correct_answer_id"],
        xp_earned=xp_earned,
    )


# ── Lesson Completion (Gap 3 + Gap 5) ─────────────────────────────────────────

class QuestionResult(BaseModel):
    question_id: str
    correct: bool
    answer_given: str
    correct_answer: Optional[str] = None


class LessonCompleteBody(BaseModel):
    score: int
    questions_attempted: List[QuestionResult] = []


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    body: LessonCompleteBody,
    current_user=Depends(get_current_user),
):
    db = get_db()
    user_id = str(current_user["_id"])
    now = datetime.datetime.utcnow()

    # Per-question accuracy + spaced repetition scaffold (Phase 3)
    progress_update = {
        "$set": {
            "completed": True,
            "score": body.score,
            "last_attempted": now,
            "questions_attempted": [q.model_dump() for q in body.questions_attempted],
            "review_schedule": {
                "next_review_date": None,
                "interval_days": 1,
                "ease_factor": 2.5,
            },
        },
        "$inc": {"attempts": 1},
    }

    await db.progress.update_one(
        {"user_id": user_id, "lesson_id": lesson_id},
        progress_update,
        upsert=True,
    )

    # Award lesson XP bonus
    lesson = await db.lessons.find_one({"id": lesson_id})
    bonus_xp = lesson.get("xp_reward", 10) if lesson else 10
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"xp": bonus_xp}}
    )

    # ── Streak tracking (Gap 5) ─────────────────────────────────────────────
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    last_activity = user.get("last_activity_date")
    current_streak = user.get("streak", 0)
    today = now.date()

    if last_activity is None:
        new_streak = 1
    else:
        last_date = last_activity.date() if hasattr(last_activity, "date") else last_activity
        delta = (today - last_date).days
        if delta == 0:
            new_streak = current_streak  # same day — no change
        elif delta == 1:
            new_streak = current_streak + 1  # consecutive day — increment
        else:
            new_streak = 1  # gap — reset

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"streak": new_streak, "last_activity_date": now}},
    )

    # ── Badge award (Phase 3) ───────────────────────────────────────────────
    # Re-fetch user to get up-to-date XP and existing badges after all updates
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    completed_count = await db.progress.count_documents({"user_id": user_id, "completed": True})
    current_xp = user.get("xp", 0)
    existing_badges = set(user.get("earned_badges", []))

    all_badges = await db.badges.find().to_list(50)
    new_badges = []
    for badge in all_badges:
        badge_id = badge.get("id") or str(badge["_id"])
        if badge_id in existing_badges:
            continue
        criteria_type = badge.get("criteria_type", "")
        criteria_value = badge.get("criteria_value", 0)

        qualifies = False
        if criteria_type == "lessons_completed" and completed_count >= criteria_value:
            qualifies = True
        elif criteria_type == "streak" and new_streak >= criteria_value:
            qualifies = True
        elif criteria_type == "xp" and current_xp >= criteria_value:
            qualifies = True
        elif criteria_type == "perfect_lesson" and body.score == 100:
            qualifies = True

        if qualifies:
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$addToSet": {"earned_badges": badge_id}},
            )
            new_badges.append({"id": badge_id, "name": badge.get("name", "Badge"), "icon": badge.get("icon", "🏆")})

    return {"message": "Lesson completed!", "xp_earned": bonus_xp, "streak": new_streak, "new_badges": new_badges}


# ── Badges (public list) ────────────────────────────────────────────────────────

@router.get("/badges")
async def list_badges():
    db = get_db()
    badges = await db.badges.find().to_list(50)
    return [
        {
            "id": b.get("id") or str(b["_id"]),
            "name": b.get("name", ""),
            "icon": b.get("icon", "🏆"),
            "criteria_type": b.get("criteria_type", ""),
            "criteria_value": b.get("criteria_value", 0),
        }
        for b in badges
    ]
