from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from auth import require_role
from routes.auth import serialize_user
from models.user import AdminUserUpdate
from bson import ObjectId
from datetime import datetime

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
