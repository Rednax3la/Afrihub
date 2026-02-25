from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth import get_current_user
from models.lesson import AnswerSubmit, AnswerResult
from bson import ObjectId

router = APIRouter(prefix="/api", tags=["lessons"])


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


# ── Units ──────────────────────────────────────────────────────────────────────

@router.get("/languages/{language_id}/units")
async def list_units(language_id: str):
    db = get_db()
    units = await db.units.find({"language_id": language_id}).sort("order", 1).to_list(50)
    for unit in units:
        unit["_id"] = str(unit["_id"])
    return units


# ── Lessons ────────────────────────────────────────────────────────────────────

@router.get("/units/{unit_id}/lessons")
async def list_lessons(unit_id: str):
    db = get_db()
    lessons = await db.lessons.find({"unit_id": unit_id}, {"questions": 0}).sort("order", 1).to_list(50)
    for lesson in lessons:
        lesson["_id"] = str(lesson["_id"])
    return lessons


@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, current_user=Depends(get_current_user)):
    db = get_db()
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    lesson["_id"] = str(lesson["_id"])
    # Strip correct answers from questions before sending
    for q in lesson.get("questions", []):
        q.pop("correct_answer_id", None)
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

    # Upsert progress record
    await db.progress.update_one(
        {"user_id": str(current_user["_id"]), "lesson_id": body.lesson_id},
        {
            "$inc": {"attempts": 1},
            "$set": {"last_attempted": __import__("datetime").datetime.utcnow()},
            "$setOnInsert": {"completed": False, "score": 0},
        },
        upsert=True
    )

    return AnswerResult(
        correct=correct,
        correct_answer_id=question["correct_answer_id"],
        xp_earned=xp_earned,
    )


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str, score: int, current_user=Depends(get_current_user)):
    """Mark a lesson as complete with a final score (0-100)."""
    db = get_db()
    import datetime

    await db.progress.update_one(
        {"user_id": str(current_user["_id"]), "lesson_id": lesson_id},
        {
            "$set": {
                "completed": True,
                "score": score,
                "last_attempted": datetime.datetime.utcnow(),
            },
            "$inc": {"attempts": 1},
        },
        upsert=True
    )

    # Award bonus XP on completion
    lesson = await db.lessons.find_one({"id": lesson_id})
    bonus_xp = lesson.get("xp_reward", 10) if lesson else 10
    await db.users.update_one(
        {"_id": ObjectId(str(current_user["_id"]))},
        {"$inc": {"xp": bonus_xp}}
    )

    return {"message": "Lesson completed!", "xp_earned": bonus_xp}
