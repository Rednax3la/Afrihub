import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from contextlib import asynccontextmanager
from database import connect_db, close_db, get_db, get_connection_status, _mask_uri
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tasks.reminders import send_streak_reminders
from routes import auth, users, lessons, progress, dictionary, payments, password_reset, foundations
from routes import admin, tutors, upload, tts

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    scheduler = AsyncIOScheduler(timezone='Africa/Nairobi')
    if os.getenv('ENABLE_STREAK_REMINDERS', 'true').lower() == 'true':
        scheduler.add_job(send_streak_reminders, 'cron', hour=19, minute=0,
                          args=[get_db()], id='streak-reminders', replace_existing=True,
                          coalesce=True, max_instances=1, misfire_grace_time=3600)
        scheduler.start()
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await close_db()


app = FastAPI(
    title="Vernaculearn API",
    description="Backend for the Vernaculearn African language learning platform",
    version="2.0.0",
    lifespan=lifespan,
)

_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,https://vernaculearn.vercel.app",
)
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def private_auth_responses(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith('/api/auth/'):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    if not request.url.path.startswith('/api/auth/'):
        return await request_validation_exception_handler(request, exc)
    # Pydantic's default response includes submitted input (passwords/tokens).
    return JSONResponse(status_code=422, content={'detail': [
        {'loc': error['loc'], 'msg': error['msg'], 'type': error['type']}
        for error in exc.errors()
    ]})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Ensure CORS headers are present even on unhandled 500 errors.
    origin = request.headers.get("origin", "")
    headers = {}
    if request.url.path.startswith('/api/auth/'):
        headers.update({'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer'})
    if origin in _allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers,
    )


# Serve uploaded media files as static assets
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(payments.router)
app.include_router(dictionary.router)
app.include_router(auth.router)
app.include_router(password_reset.router)
app.include_router(foundations.router)
app.include_router(users.router)
app.include_router(lessons.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(tutors.router)
app.include_router(upload.router)
app.include_router(tts.router)


@app.get("/")
async def root():
    status = get_connection_status()
    mongodb_uri = os.getenv("MONGODB_URI")

    if not mongodb_uri:
        db_status = "❌ MONGODB_URI is not set"
    elif status["connected"]:
        db_status = f"✅ Connected ({_mask_uri(mongodb_uri)})"
    else:
        db_status = f"❌ Connection failed: {status['error']} ({_mask_uri(mongodb_uri)})"

    return {
        "message": "🌍 Vernaculearn API is running",
        "docs": "/docs",
        "mongodb_status": db_status,
        "mongodb_connected": status["connected"],
    }


@app.get("/api/admin/seed")
async def run_seed(key: str):
    import traceback
    seed_key = os.getenv("SEED_KEY", "")
    if not seed_key or key != seed_key:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        from database import get_db
        from auth import hash_password
        from seed import LANGUAGES, UNITS, LESSONS, USERS, BADGES, CULTURAL_NOTES
        from datetime import datetime
        db = get_db()
        await db.languages.drop()
        await db.units.drop()
        await db.lessons.drop()
        await db.badges.drop()
        await db.cultural_notes.drop()
        await db.languages.insert_many(LANGUAGES)
        await db.units.insert_many(UNITS)
        await db.lessons.insert_many(LESSONS)
        await db.badges.insert_many(BADGES)
        await db.cultural_notes.insert_many(CULTURAL_NOTES)
        for u in USERS:
            u["created_at"] = datetime.utcnow()
            if u["name"] == "Admin":
                u["password_hash"] = hash_password("Admin1234!")
            else:
                u["password_hash"] = hash_password("Tutor1234!")
            await db.users.update_one({"email": u["email"]}, {"$set": u}, upsert=True)
        return {"message": "Database seeded successfully"}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
