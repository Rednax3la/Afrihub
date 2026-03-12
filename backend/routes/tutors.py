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
