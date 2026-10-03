from fastapi import APIRouter, Depends
from database import get_db, log_timing
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

    with log_timing("get_my_progress total"):
        return await _build_my_progress(db, user_id, current_user)


async def _build_my_progress(db, user_id: str, current_user: dict):
    # Grab all progress docs for this user
    with log_timing("get_my_progress progress query"):
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

    # Batch fetch languages, units and lessons for all active languages
    # (3 queries total instead of 1 + N units per language).
    languages_by_id = {}
    unit_to_lang = {}
    lessons_by_lang = {}
    if active_lang_ids:
        with log_timing("get_my_progress languages/units/lessons queries"):
            languages = await db.languages.find({"id": {"$in": active_lang_ids}}).to_list(None)
            languages_by_id = {l["id"]: l for l in languages}
            units = await db.units.find(
                {"language_id": {"$in": active_lang_ids}}, {"id": 1, "language_id": 1}
            ).to_list(None)
            unit_to_lang = {u["id"]: u["language_id"] for u in units}
            if unit_to_lang:
                lessons = await db.lessons.find(
                    {"unit_id": {"$in": list(unit_to_lang.keys())}}, {"id": 1, "unit_id": 1}
                ).to_list(None)
                for lesson in lessons:
                    lessons_by_lang.setdefault(unit_to_lang[lesson["unit_id"]], []).append(lesson["id"])

    for lang_id in active_lang_ids:
        language = languages_by_id.get(lang_id)
        if not language:
            continue

        lesson_ids = lessons_by_lang.get(lang_id, [])
        total_lessons = len(lesson_ids)
        completed_lessons = sum(
            1 for lid in lesson_ids
            if progress_map.get(lid, {}).get("completed")
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

    language_progress = {
        lang["language_id"]: lang["completed_lessons"]
        for lang in languages_summary
    }

    return {
        "user_id": user_id,
        "total_xp": current_user.get("xp", 0),
        "streak": current_user.get("streak", 0),
        "languages": languages_summary,
        "lesson_progress": progress_map,
        "language_progress": language_progress,
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


@router.get('/me/due-for-review')
async def due_for_review(current_user=Depends(get_current_user)):
    from services.reviews import today_eat
    from services.subscriptions import has_active_subscription
    db = get_db()
    pipeline = [
        {'$match': {'user_id': str(current_user['_id']), 'review_schedule.next_review_date': {'$type': 'string', '$lte': today_eat().isoformat()}}},
        {'$sort': {'review_schedule.next_review_date': 1}},
        {'$lookup': {'from': 'lessons', 'localField': 'lesson_id', 'foreignField': 'id', 'as': 'lesson'}},
        {'$unwind': '$lesson'},
        {'$match': {'lesson.status': {'$nin': ['draft', 'rejected', 'pending_review']}}},
        {'$lookup': {'from': 'units', 'localField': 'lesson.unit_id', 'foreignField': 'id', 'as': 'unit'}},
        {'$unwind': '$unit'},
    ]
    pipeline.extend([
        {'$lookup': {'from': 'languages', 'localField': 'unit.language_id', 'foreignField': 'id', 'as': 'language'}},
        {'$unwind': '$language'},
        {'$project': {'_id': 0, 'lesson_id': 1, 'title': '$lesson.title', 'language_id': '$language.id', 'language_name': '$language.name', 'review_schedule': 1, 'locked': {'$and': [{'$gt': ['$unit.order', 3]}, {'$literal': not has_active_subscription(current_user)}]}}},
    ])
    return await db.progress.aggregate(pipeline).to_list(None)
