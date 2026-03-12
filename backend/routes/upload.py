import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
ALLOWED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".webm"}
ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_SIZE = 15 * 1024 * 1024  # 15 MB


@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_AUDIO:
        raise HTTPException(400, f"Unsupported format. Allowed: {', '.join(ALLOWED_AUDIO)}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 15 MB)")

    dest = os.path.join(UPLOAD_DIR, "audio")
    os.makedirs(dest, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    async with aiofiles.open(os.path.join(dest, filename), "wb") as f:
        await f.write(content)

    return {"url": f"/uploads/audio/{filename}", "filename": filename}


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE:
        raise HTTPException(400, f"Unsupported format. Allowed: {', '.join(ALLOWED_IMAGE)}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 15 MB)")

    dest = os.path.join(UPLOAD_DIR, "image")
    os.makedirs(dest, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    async with aiofiles.open(os.path.join(dest, filename), "wb") as f:
        await f.write(content)

    return {"url": f"/uploads/image/{filename}", "filename": filename}
