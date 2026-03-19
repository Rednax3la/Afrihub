import os
import uuid
import asyncio
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
ALLOWED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".webm"}
ALLOWED_IMAGE = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_SIZE = 15 * 1024 * 1024  # 15 MB

R2_ENABLED = os.getenv("R2_ENABLED", "false").lower() == "true"


def _get_r2_client():
    import boto3
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


async def _upload_to_r2(content: bytes, key: str, content_type: str) -> str:
    bucket = os.getenv("R2_BUCKET_NAME", "vernaculearn-media")
    public_url = os.getenv("R2_PUBLIC_URL", "").rstrip("/")

    def _sync():
        _get_r2_client().put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
        )

    await asyncio.to_thread(_sync)
    return f"{public_url}/{key}"


async def _upload_local(content: bytes, subdir: str, filename: str, request: Request) -> str:
    dest = os.path.join(UPLOAD_DIR, subdir)
    os.makedirs(dest, exist_ok=True)
    async with aiofiles.open(os.path.join(dest, filename), "wb") as f:
        await f.write(content)
    # Return absolute URL so it works when frontend and backend are on different domains
    base = str(request.base_url).rstrip("/")
    return f"{base}/uploads/{subdir}/{filename}"


@router.post("/audio")
async def upload_audio(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_AUDIO:
        raise HTTPException(400, f"Unsupported format. Allowed: {', '.join(ALLOWED_AUDIO)}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 15 MB)")

    filename = f"{uuid.uuid4()}{ext}"
    if R2_ENABLED:
        url = await _upload_to_r2(content, f"audio/{filename}", file.content_type or "audio/mpeg")
    else:
        url = await _upload_local(content, "audio", filename, request)

    return {"url": url, "filename": filename}


@router.post("/image")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_IMAGE:
        raise HTTPException(400, f"Unsupported format. Allowed: {', '.join(ALLOWED_IMAGE)}")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 15 MB)")

    filename = f"{uuid.uuid4()}{ext}"
    if R2_ENABLED:
        url = await _upload_to_r2(content, f"image/{filename}", file.content_type or "image/jpeg")
    else:
        url = await _upload_local(content, "image", filename, request)

    return {"url": url, "filename": filename}
