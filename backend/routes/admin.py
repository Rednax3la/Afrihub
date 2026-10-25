from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth import require_role
from routes.auth import serialize_user
from models.user import AdminPremiumUpdate, AdminUserUpdate
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/api/admin", tags=["admin"])

_admin = require_role("admin")


def _serialize_language(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


def _serialize_unit(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


def _serialize_lesson(doc: dict) -> dict:
    doc = dict(doc)
    doc.pop("_id", None)
    return doc


# ── Stats ──────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def get_stats(admin=Depends(_admin)):
    db = get_db()
    total_students = await db.users.count_documents({"role": {"$in": ["student", None]}})
    total_tutors = await db.users.count_documents({"role": "tutor"})
    pending_tutors = await db.users.count_documents({"role": "tutor", "tutor_status": "pending"})
    total_languages = await db.languages.count_documents({})
    total_units = await db.units.count_documents({})
    total_lessons = await db.lessons.count_documents({})
    return {
        "total_students": total_students,
        "total_tutors": total_tutors,
        "pending_tutors": pending_tutors,
        "total_languages": total_languages,
        "total_units": total_units,
        "total_lessons": total_lessons,
    }


# ── Users ──────────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(admin=Depends(_admin)):
    db = get_db()
    users = await db.users.find({"role": {"$in": ["student", None]}}).sort("created_at", -1).to_list(500)
    return [serialize_user(u) for u in users]


@router.patch("/users/{user_id}/premium")
async def set_user_premium(user_id: str, body: AdminPremiumUpdate, admin=Depends(_admin)):
    """Grant or revoke premium access.

    Writes the fields the paywall and serialize_user actually read
    (subscription_status / subscription_tier / expires_at / admin_granted).
    The old PATCH /users/{id} path wrote a standalone `is_premium` boolean that
    nothing consumed, which is why grants appeared to succeed and changed
    nothing.
    """
    db = get_db()
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(400, "Invalid user id")

    if body.granted:
        expires_at = body.expires_at
        if expires_at is not None:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at <= datetime.now(timezone.utc):
                raise HTTPException(422, "expires_at must be in the future")
        update = {
            "subscription_status": "active",
            "subscription_tier": "admin_grant",
            "admin_granted": True,
            "expires_at": expires_at,
            "admin_grant_note": body.note,
            "admin_grant_by": str(admin["_id"]),
            "admin_grant_at": datetime.now(timezone.utc),
        }
    else:
        update = {
            "subscription_status": "inactive",
            "admin_granted": False,
            "admin_grant_note": body.note,
            "admin_grant_by": str(admin["_id"]),
            "admin_grant_at": datetime.now(timezone.utc),
        }

    result = await db.users.update_one({"_id": oid}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "User not found")
    updated = await db.users.find_one({"_id": oid})
    return serialize_user(updated)


@router.patch("/users/{user_id}")
async def update_user(user_id: str, body: AdminUserUpdate, admin=Depends(_admin)):
    db = get_db()
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(400, "No fields to update")
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated = await db.users.find_one({"_id": ObjectId(user_id)})
    if not updated:
        raise HTTPException(404, "User not found")
    return serialize_user(updated)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str, admin=Depends(_admin)):
    db = get_db()
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "User not found")


# ── Tutors ─────────────────────────────────────────────────────────────────────

@router.get("/tutors")
async def list_tutors(admin=Depends(_admin)):
    db = get_db()
    tutors = await db.users.find({"role": "tutor"}).sort("created_at", -1).to_list(200)
    return [serialize_user(t) for t in tutors]


@router.patch("/tutors/{tutor_id}/approve")
async def approve_tutor(tutor_id: str, admin=Depends(_admin)):
    db = get_db()
    await db.users.update_one({"_id": ObjectId(tutor_id)}, {"$set": {"tutor_status": "active"}})
    tutor = await db.users.find_one({"_id": ObjectId(tutor_id)})
    if not tutor:
        raise HTTPException(404, "Tutor not found")
    return serialize_user(tutor)


@router.patch("/tutors/{tutor_id}/suspend")
async def suspend_tutor(tutor_id: str, admin=Depends(_admin)):
    db = get_db()
    await db.users.update_one({"_id": ObjectId(tutor_id)}, {"$set": {"tutor_status": "suspended"}})
    tutor = await db.users.find_one({"_id": ObjectId(tutor_id)})
    if not tutor:
        raise HTTPException(404, "Tutor not found")
    return serialize_user(tutor)


# ── Languages ──────────────────────────────────────────────────────────────────

@router.get("/languages")
async def list_languages(admin=Depends(_admin)):
    db = get_db()
    langs = await db.languages.find({}).to_list(200)
    return [_serialize_language(l) for l in langs]


@router.post("/languages", status_code=201)
async def create_language(body: dict, admin=Depends(_admin)):
    db = get_db()
    existing = await db.languages.find_one({"id": body.get("id")})
    if existing:
        raise HTTPException(400, "Language with this id already exists")
    result = await db.languages.insert_one(body)
    body.pop("_id", None)
    return body


@router.patch("/languages/{lang_id}")
async def update_language(lang_id: str, body: dict, admin=Depends(_admin)):
    db = get_db()
    body.pop("_id", None)
    await db.languages.update_one({"id": lang_id}, {"$set": body})
    lang = await db.languages.find_one({"id": lang_id})
    if not lang:
        raise HTTPException(404, "Language not found")
    return _serialize_language(lang)


@router.delete("/languages/{lang_id}", status_code=204)
async def delete_language(lang_id: str, admin=Depends(_admin)):
    db = get_db()
    await db.languages.delete_one({"id": lang_id})


# ── Units ──────────────────────────────────────────────────────────────────────

@router.get("/units")
async def list_units(admin=Depends(_admin), language_id: str = None):
    db = get_db()
    query = {"language_id": language_id} if language_id else {}
    units = await db.units.find(query).sort("order", 1).to_list(500)
    return [_serialize_unit(u) for u in units]


@router.post("/units", status_code=201)
async def create_unit(body: dict, admin=Depends(_admin)):
    db = get_db()
    body.pop("_id", None)
    result = await db.units.insert_one(body)
    body.pop("_id", None)
    return body


@router.patch("/units/{unit_id}")
async def update_unit(unit_id: str, body: dict, admin=Depends(_admin)):
    db = get_db()
    body.pop("_id", None)
    await db.units.update_one({"id": unit_id}, {"$set": body})
    unit = await db.units.find_one({"id": unit_id})
    if not unit:
        raise HTTPException(404, "Unit not found")
    return _serialize_unit(unit)


@router.delete("/units/{unit_id}", status_code=204)
async def delete_unit(unit_id: str, admin=Depends(_admin)):
    db = get_db()
    await db.units.delete_one({"id": unit_id})


# ── Lessons ────────────────────────────────────────────────────────────────────

@router.get("/lessons")
async def list_lessons(admin=Depends(_admin), unit_id: str = None):
    db = get_db()
    query = {"unit_id": unit_id} if unit_id else {}
    lessons = await db.lessons.find(query).sort("order", 1).to_list(1000)
    return [_serialize_lesson(l) for l in lessons]


@router.post("/lessons", status_code=201)
async def create_lesson(body: dict, admin=Depends(_admin)):
    db = get_db()
    body.pop("_id", None)
    if "questions" not in body:
        body["questions"] = []
    result = await db.lessons.insert_one(body)
    body.pop("_id", None)
    return body


@router.patch("/lessons/{lesson_id}")
async def update_lesson(lesson_id: str, body: dict, admin=Depends(_admin)):
    db = get_db()
    body.pop("_id", None)
    await db.lessons.update_one({"id": lesson_id}, {"$set": body})
    lesson = await db.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return _serialize_lesson(lesson)


@router.delete("/lessons/{lesson_id}", status_code=204)
async def delete_lesson(lesson_id: str, admin=Depends(_admin)):
    db = get_db()
    await db.lessons.delete_one({"id": lesson_id})


# ── Review Queue (2E) ──────────────────────────────────────────────────────────

@router.get("/review-queue/stats")
async def review_queue_stats(admin=Depends(_admin)):
    db = get_db()
    pipeline = [
        {"$match": {"status": "pending_review"}},
        {"$group": {"_id": "$language_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    rows = await db.lessons.aggregate(pipeline).to_list(100)
    total = sum(r["count"] for r in rows)
    audio_pending = await db.audio_submissions.count_documents({"status": "pending_review"})
    return {
        "total": total,
        "by_language": {r["_id"]: r["count"] for r in rows},
        "audio_pending": audio_pending,
    }


async def _tutor_names(db, tutor_ids: set[str]) -> dict:
    """Resolve tutor_id -> display name for the review queue."""
    oids = []
    for tid in tutor_ids:
        try:
            oids.append(ObjectId(tid))
        except Exception:
            continue
    if not oids:
        return {}
    rows = await db.users.find({"_id": {"$in": oids}}, {"name": 1}).to_list(len(oids))
    return {str(r["_id"]): r.get("name", "Unknown tutor") for r in rows}


@router.get("/review-queue")
async def get_review_queue(admin=Depends(_admin)):
    db = get_db()
    lessons = await db.lessons.find({"status": "pending_review"}).sort("language_id", 1).to_list(500)
    names = await _tutor_names(db, {l["tutor_id"] for l in lessons if l.get("tutor_id")})
    grouped: dict = {}
    for lesson in lessons:
        lesson.pop("_id", None)
        if lesson.get("tutor_id"):
            lesson.setdefault("tutor_name", names.get(lesson["tutor_id"], "Unknown tutor"))
        grouped.setdefault(lesson.get("language_id", "unknown"), []).append(lesson)
    return grouped


@router.get("/review-queue/audio")
async def get_audio_review_queue(admin=Depends(_admin)):
    """Tutor-submitted recordings awaiting approval, with lesson context."""
    db = get_db()
    rows = await db.audio_submissions.find(
        {"status": "pending_review"}
    ).sort("submitted_at", 1).to_list(500)
    names = await _tutor_names(db, {r["tutor_id"] for r in rows if r.get("tutor_id")})
    for row in rows:
        row["_id"] = str(row["_id"])
        row["tutor_name"] = row.get("tutor_name") or names.get(row.get("tutor_id"), "Unknown tutor")
    return rows


def _audio_filter(submission_id: str) -> dict:
    try:
        return {"_id": ObjectId(submission_id)}
    except Exception:
        raise HTTPException(400, "Invalid submission id")


@router.patch("/review-queue/audio/{submission_id}/approve")
async def approve_audio(submission_id: str, admin=Depends(_admin)):
    """Approving is what actually writes audio_url onto the question."""
    db = get_db()
    submission = await db.audio_submissions.find_one(_audio_filter(submission_id))
    if not submission:
        raise HTTPException(404, "Submission not found")
    result = await db.lessons.update_one(
        {"id": submission["lesson_id"], "questions.id": submission["question_id"]},
        {"$set": {"questions.$.audio_url": submission["audio_url"]}},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "The question this recording belongs to no longer exists")
    await db.audio_submissions.update_one(
        {"_id": submission["_id"]},
        {"$set": {
            "status": "approved",
            "reviewed_by": str(admin["_id"]),
            "reviewed_at": datetime.now(timezone.utc),
            "rejection_reason": None,
        }},
    )
    return {"status": "approved", "lesson_id": submission["lesson_id"],
            "question_id": submission["question_id"], "audio_url": submission["audio_url"]}


@router.patch("/review-queue/audio/{submission_id}/reject")
async def reject_audio(submission_id: str, body: dict | None = None, admin=Depends(_admin)):
    db = get_db()
    result = await db.audio_submissions.update_one(
        _audio_filter(submission_id),
        {"$set": {
            "status": "rejected",
            "reviewed_by": str(admin["_id"]),
            "reviewed_at": datetime.now(timezone.utc),
            "rejection_reason": (body or {}).get("reason"),
        }},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Submission not found")
    return {"status": "rejected"}


@router.patch("/lessons/{lesson_id}/approve")
async def approve_lesson(lesson_id: str, admin=Depends(_admin)):
    db = get_db()
    result = await db.lessons.update_one(
        {"id": lesson_id},
        {"$set": {"status": "published", "reviewed_by": str(admin["_id"]),
                  "reviewed_at": datetime.now(timezone.utc)},
         "$unset": {"rejection_reason": ""}},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Lesson not found")
    return _serialize_lesson(await db.lessons.find_one({"id": lesson_id}))


@router.patch("/lessons/{lesson_id}/reject")
async def reject_lesson(lesson_id: str, body: dict | None = None, admin=Depends(_admin)):
    db = get_db()
    result = await db.lessons.update_one(
        {"id": lesson_id},
        {"$set": {"status": "rejected", "reviewed_by": str(admin["_id"]),
                  "reviewed_at": datetime.now(timezone.utc),
                  "rejection_reason": (body or {}).get("reason")}},
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Lesson not found")
    return _serialize_lesson(await db.lessons.find_one({"id": lesson_id}))
