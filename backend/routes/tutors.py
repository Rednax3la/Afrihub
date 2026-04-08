from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth import get_current_user, require_active_tutor
from routes.auth import serialize_user
from bson import ObjectId

router = APIRouter(prefix="/api/tutors", tags=["tutors"])

_active_tutor = require_active_tutor()


def _serialize_unit(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


def _serialize_lesson(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


# ── Public endpoints ───────────────────────────────────────────────────────────

@router.get("/")
async def list_active_tutors():
    db = get_db()
    tutors = await db.users.find(
        {"role": "tutor", "tutor_status": "active"}
    ).to_list(50)
    return [serialize_user(t) for t in tutors]


@router.get("/{tutor_id}")
async def get_tutor(tutor_id: str):
    db = get_db()
    try:
        tutor = await db.users.find_one({"_id": ObjectId(tutor_id), "role": "tutor"})
    except Exception:
        raise HTTPException(400, "Invalid tutor ID")
    if not tutor:
        raise HTTPException(404, "Tutor not found")
    return serialize_user(tutor)


# ── Authenticated tutor routes ─────────────────────────────────────────────────

@router.get("/me/profile")
async def get_my_profile(tutor=Depends(_active_tutor)):
    return serialize_user(tutor)


@router.patch("/me/profile")
async def update_my_profile(body: dict, tutor=Depends(_active_tutor)):
    db = get_db()
    allowed = {"bio", "avatar_url", "voice_character", "location", "name", "languages_taught"}
    update_data = {k: v for k, v in body.items() if k in allowed}
    if not update_data:
        return serialize_user(tutor)
    await db.users.update_one({"_id": tutor["_id"]}, {"$set": update_data})
    updated = await db.users.find_one({"_id": tutor["_id"]})
    return serialize_user(updated)


@router.get("/me/content")
async def get_my_content(tutor=Depends(_active_tutor)):
    db = get_db()
    tutor_id = str(tutor["_id"])
    units = await db.units.find({"tutor_id": tutor_id}).sort("order", 1).to_list(100)
    lessons = await db.lessons.find({"tutor_id": tutor_id}).sort("order", 1).to_list(500)
    return {
        "units": [_serialize_unit(u) for u in units],
        "lessons": [_serialize_lesson(l) for l in lessons],
    }


@router.post("/me/units", status_code=201)
async def create_unit(body: dict, tutor=Depends(_active_tutor)):
    db = get_db()
    body.pop("_id", None)
    body["tutor_id"] = str(tutor["_id"])
    result = await db.units.insert_one(body)
    body.pop("_id", None)
    return body


@router.patch("/me/units/{unit_id}")
async def update_unit(unit_id: str, body: dict, tutor=Depends(_active_tutor)):
    db = get_db()
    tutor_id = str(tutor["_id"])
    existing = await db.units.find_one({"id": unit_id})
    if not existing or existing.get("tutor_id") != tutor_id:
        raise HTTPException(403, "You do not own this unit")
    body.pop("_id", None)
    await db.units.update_one({"id": unit_id}, {"$set": body})
    unit = await db.units.find_one({"id": unit_id})
    return _serialize_unit(unit)


@router.post("/me/lessons", status_code=201)
async def create_lesson(body: dict, tutor=Depends(_active_tutor)):
    db = get_db()
    body.pop("_id", None)
    body["tutor_id"] = str(tutor["_id"])
    if "questions" not in body:
        body["questions"] = []
    result = await db.lessons.insert_one(body)
    body.pop("_id", None)
    return body


@router.patch("/me/lessons/{lesson_id}")
async def update_lesson(lesson_id: str, body: dict, tutor=Depends(_active_tutor)):
    db = get_db()
    tutor_id = str(tutor["_id"])
    existing = await db.lessons.find_one({"id": lesson_id})
    if not existing or existing.get("tutor_id") != tutor_id:
        raise HTTPException(403, "You do not own this lesson")
    body.pop("_id", None)
    await db.lessons.update_one({"id": lesson_id}, {"$set": body})
    lesson = await db.lessons.find_one({"id": lesson_id})
    return _serialize_lesson(lesson)


@router.delete("/me/lessons/{lesson_id}", status_code=204)
async def delete_lesson(lesson_id: str, tutor=Depends(_active_tutor)):
    db = get_db()
    tutor_id = str(tutor["_id"])
    existing = await db.lessons.find_one({"id": lesson_id})
    if not existing or existing.get("tutor_id") != tutor_id:
        raise HTTPException(403, "You do not own this lesson")
    await db.lessons.delete_one({"id": lesson_id})


@router.delete("/me/units/{unit_id}", status_code=204)
async def delete_unit(unit_id: str, tutor=Depends(_active_tutor)):
    db = get_db()
    tutor_id = str(tutor["_id"])
    existing = await db.units.find_one({"id": unit_id})
    if not existing or existing.get("tutor_id") != tutor_id:
        raise HTTPException(403, "You do not own this unit")
    await db.units.delete_one({"id": unit_id})


# ── Review Queue (2E) ──────────────────────────────────────────────────────────

@router.get("/me/review-queue")
async def get_review_queue(tutor=Depends(_active_tutor)):
    db = get_db()
    languages_taught = tutor.get("languages_taught", [])
    lessons = await db.lessons.find(
        {"status": "pending_review", "language_id": {"$in": languages_taught}}
    ).sort("language_id", 1).to_list(200)
    grouped: dict = {}
    for lesson in lessons:
        lesson.pop("_id", None)
        lang = lesson.get("language_id", "unknown")
        grouped.setdefault(lang, []).append(lesson)
    return grouped


@router.get("/me/review-queue/count")
async def get_review_queue_count(tutor=Depends(_active_tutor)):
    db = get_db()
    languages_taught = tutor.get("languages_taught", [])
    count = await db.lessons.count_documents(
        {"status": "pending_review", "language_id": {"$in": languages_taught}}
    )
    return {"count": count}


@router.patch("/me/review/{lesson_id}/approve")
async def tutor_approve_lesson(lesson_id: str, tutor=Depends(_active_tutor)):
    db = get_db()
    languages_taught = tutor.get("languages_taught", [])
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    if lesson.get("language_id") not in languages_taught:
        raise HTTPException(403, "This lesson is not in your languages")
    await db.lessons.update_one({"id": lesson_id}, {"$set": {"status": "published"}})
    lesson = await db.lessons.find_one({"id": lesson_id})
    return _serialize_lesson(lesson)


@router.patch("/me/review/{lesson_id}/reject")
async def tutor_reject_lesson(lesson_id: str, tutor=Depends(_active_tutor)):
    db = get_db()
    languages_taught = tutor.get("languages_taught", [])
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    if lesson.get("language_id") not in languages_taught:
        raise HTTPException(403, "This lesson is not in your languages")
    await db.lessons.update_one({"id": lesson_id}, {"$set": {"status": "rejected"}})
    lesson = await db.lessons.find_one({"id": lesson_id})
    return _serialize_lesson(lesson)


# ── Cultural Notes (2C) ────────────────────────────────────────────────────────

@router.post("/me/cultural-notes", status_code=201)
async def create_cultural_note(body: dict, tutor=Depends(_active_tutor)):
    db = get_db()
    body.pop("_id", None)
    body["tutor_id"] = str(tutor["_id"])
    body.setdefault("source", "tutor")
    result = await db.cultural_notes.insert_one(body)
    body["_id"] = str(result.inserted_id)
    return body


@router.patch("/me/cultural-notes/{note_id}")
async def update_cultural_note(note_id: str, body: dict, tutor=Depends(_active_tutor)):
    db = get_db()
    from bson import ObjectId as ObjId
    tutor_id = str(tutor["_id"])
    try:
        existing = await db.cultural_notes.find_one({"_id": ObjId(note_id)})
    except Exception:
        raise HTTPException(400, "Invalid note ID")
    if not existing or existing.get("tutor_id") != tutor_id:
        raise HTTPException(403, "You do not own this cultural note")
    body.pop("_id", None)
    await db.cultural_notes.update_one({"_id": ObjId(note_id)}, {"$set": body})
    note = await db.cultural_notes.find_one({"_id": ObjId(note_id)})
    note["_id"] = str(note["_id"])
    return note


# ── Recording Queue ────────────────────────────────────────────────────────────

@router.get("/me/recording-queue")
async def get_recording_queue(tutor=Depends(_active_tutor)):
    """
    Returns published lessons for the tutor's languages where at least one
    question has audio_url == null. Groups by lesson, shows only the
    questions that need recording.
    """
    db = get_db()
    languages_taught = tutor.get("languages_taught", [])

    lessons = await db.lessons.find({
        "language_id": {"$in": languages_taught},
        "status": {"$nin": ["draft", "rejected", "pending_review"]},
    }).sort("language_id", 1).to_list(500)

    queue = []
    for lesson in lessons:
        needs_audio = [
            q for q in lesson.get("questions", [])
            if q.get("audio_url") is None
            and q.get("type") in ("translate", "multiple_choice", "listen", "listen_comprehension")
        ]
        if needs_audio:
            queue.append({
                "lesson_id": lesson["id"],
                "lesson_title": lesson.get("title", ""),
                "language_id": lesson.get("language_id", ""),
                "unit_id": lesson.get("unit_id", ""),
                "total_questions": len(lesson.get("questions", [])),
                "needs_recording": len(needs_audio),
                "questions": [
                    {
                        "question_id": q["id"],
                        "type": q["type"],
                        "prompt": q.get("prompt", ""),
                        "native_text": q.get("native_text", ""),
                    }
                    for q in needs_audio
                ],
            })

    return {
        "total_pending": sum(item["needs_recording"] for item in queue),
        "lessons": queue,
    }


@router.patch("/me/recording/{lesson_id}/{question_id}")
async def submit_recording(
    lesson_id: str,
    question_id: str,
    body: dict,
    tutor=Depends(_active_tutor),
):
    """
    Tutor submits an audio_url for a specific question.
    Body: { "audio_url": "https://..." }
    """
    db = get_db()
    audio_url = body.get("audio_url")
    if not audio_url:
        raise HTTPException(400, "audio_url is required")

    languages_taught = tutor.get("languages_taught", [])
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    if lesson.get("language_id") not in languages_taught:
        raise HTTPException(403, "This lesson is not in your languages")

    result = await db.lessons.update_one(
        {"id": lesson_id, "questions.id": question_id},
        {"$set": {"questions.$.audio_url": audio_url}}
    )
    if result.modified_count == 0:
        raise HTTPException(404, "Question not found in this lesson")

    return {"message": "Recording submitted", "lesson_id": lesson_id, "question_id": question_id}
