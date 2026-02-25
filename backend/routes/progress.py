from fastapi import APIRouter, Depends
from database import get_db
from auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/me")
async def get_my_progress(current_user=Depends(get_current_user)):
    """
    Returns the authenticated user's lesson progress across all languages.
    """
    db = get_db()
    user_id = str(current_user["_id"])

    # Grab all progress docs for this user
    progress_docs = await db.progress.find({"user_id": user_id}).to_list(500)

    # Build a summary keyed by lesson_id
    progress_map = {
        doc["lesson_id"]: {
            "completed": doc.get("completed", False),
            "score": doc.get("score", 0),
            "attempts": doc.get("attempts", 0),
        }
        for doc in progress_docs
    }

    # Aggregate by language
    languages_summary = []
    active_lang_ids = current_user.get("active_languages", [])

    for lang_id in active_lang_ids:
        language = await db.languages.find_one({"id": lang_id})
        if not language:
            continue

        units = await db.units.find({"language_id": lang_id}).to_list(50)
        total_lessons = 0
        completed_lessons = 0

        for unit in units:
            lessons = await db.lessons.find(
                {"unit_id": unit["id"]}, {"id": 1}
            ).to_list(50)
            total_lessons += len(lessons)
            completed_lessons += sum(
                1 for l in lessons
                if progress_map.get(l["id"], {}).get("completed")
            )

        pct = round((completed_lessons / total_lessons * 100), 1) if total_lessons else 0.0

        languages_summary.append({
            "language_id": lang_id,
            "language_name": language["name"],
            "flag_emoji": language["flag_emoji"],
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "percent_complete": pct,
        })

    return {
        "user_id": user_id,
        "total_xp": current_user.get("xp", 0),
        "streak": current_user.get("streak", 0),
        "languages": languages_summary,
        "lesson_progress": progress_map,
    }


@router.get("/me/lesson/{lesson_id}")
async def get_lesson_progress(lesson_id: str, current_user=Depends(get_current_user)):
    """Returns progress for a specific lesson."""
    db = get_db()
    doc = await db.progress.find_one({
        "user_id": str(current_user["_id"]),
        "lesson_id": lesson_id,
    })
    if not doc:
        return {"lesson_id": lesson_id, "completed": False, "score": 0, "attempts": 0}

    return {
        "lesson_id": lesson_id,
        "completed": doc.get("completed", False),
        "score": doc.get("score", 0),
        "attempts": doc.get("attempts", 0),
    }
