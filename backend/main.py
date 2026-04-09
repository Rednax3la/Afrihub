import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import connect_db, close_db
from routes import auth, users, lessons, progress
from routes import admin, tutors, upload, tts


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
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


# Ensure CORS headers are present even on unhandled 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    headers = {}
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

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lessons.router)
app.include_router(progress.router)
app.include_router(admin.router)
app.include_router(tutors.router)
app.include_router(upload.router)
app.include_router(tts.router)


@app.get("/")
async def root():
    return {
        "message": "🌍 Vernaculearn API is running",
        "docs": "/docs",
        "mongodb_uri": os.getenv("MONGODB_URI", "NOT SET"),
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
